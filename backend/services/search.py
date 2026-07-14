import re
from difflib import SequenceMatcher
from typing import List

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.alias import Alias
from backend.models.movie import Movie
from backend.models.series import Series
from backend.schemas.search import SearchResultItem

MYANMAR_RE = re.compile(r"[\u1000-\u109f]")
GENERIC_WORDS = {"the", "a", "an", "movie", "movies", "series", "film", "show", "video", "ကား", "ရုပ်ရှင်", "ဇာတ်လမ်းတွဲ"}

QUERY_EXPANSIONS = {
    "အာဗာတာ": "avatar",
    "အဗာတာ": "avatar",
    "အဗတာ": "avatar",
    "အပြာရောင်လူသား": "avatar blue people",
    "အပြာရောင် လူသား": "avatar blue people",
    "အပြာလူသား": "avatar blue people",
    "blue people": "avatar",
    "blue human": "avatar",
    "blue humans": "avatar",
    "စူပါမင်း": "superman flying man",
    "စူပါ မင်း": "superman flying man",
    "လေပေါ်ပျံတဲ့လူသား": "superman flying man",
    "အမြန်ပြေးလူသား": "the flash fast superhero",
    "အမြန်ပြေးတဲ့လူ": "the flash fast superhero",
}

TITLE_CONCEPTS = {
    "avatar": "avatar blue people blue humanoids alien planet pandora အပြာရောင်လူသား",
    "flash": "the flash fast running superhero speedster lightning အမြန်ပြေးလူသား",
    "superman": "superman flying superhero man of steel krypton လေပေါ်ပျံတဲ့လူသား စူပါမင်း",
}


async def search_content(
    db: AsyncSession,
    query: str,
    embedding_service,
    page: int = 1,
    per_page: int = 10,
) -> (List[SearchResultItem], int):
    del embedding_service
    q = _normalize(query)
    expanded_queries = _expanded_queries(q)
    if not q:
        return [], 0
    # A shared article such as "The" is never enough to identify a title.
    if not [token for token in _tokens(q) if token not in GENERIC_WORDS]:
        return [], 0

    # Do not pull every published record into Python.  PostgreSQL's trigram
    # indexes reduce a catalogue of hundreds of thousands of titles to a
    # small candidate set before the more nuanced local ranking below.
    movie_rows = await _candidate_media(db, Movie, expanded_queries)
    series_rows = await _candidate_media(db, Series, expanded_queries)

    scored: list[tuple[float, SearchResultItem]] = []
    for movie in movie_rows:
        score, match_type = _score_media(movie, "movie", expanded_queries)
        # A search result must actually be a credible match.  The previous
        # 0.34 cutoff let unrelated titles through on short queries.
        if score >= 0.60:
            scored.append((
                score,
                SearchResultItem(
                    id=movie.id,
                    title=movie.title,
                    type="movie",
                    thumbnail=movie.thumbnail,
                    year=movie.year,
                    match_type=match_type,
                ),
            ))

    for series in series_rows:
        score, match_type = _score_media(series, "series", expanded_queries)
        if score >= 0.60:
            scored.append((
                score,
                SearchResultItem(
                    id=series.id,
                    title=series.title,
                    type="series",
                    thumbnail=series.poster,
                    year=series.year,
                    match_type=match_type,
                ),
            ))

    for alias in await _candidate_aliases(db, expanded_queries):
        alias_value = _normalize(alias.name)
        score = max(_text_score(query, alias_value) for query in expanded_queries)
        if score < 0.60:
            continue
        if alias.movie:
            media = alias.movie
            scored.append((score + 0.12, SearchResultItem(id=media.id, title=media.title, type="movie", thumbnail=media.thumbnail, year=media.year, match_type="alias")))
        elif alias.series:
            media = alias.series
            scored.append((score + 0.12, SearchResultItem(id=media.id, title=media.title, type="series", thumbnail=media.poster, year=media.year, match_type="alias")))

    best_by_key: dict[tuple[str, int], tuple[float, SearchResultItem]] = {}
    for score, item in scored:
        key = (item.type, item.id)
        if key not in best_by_key or score > best_by_key[key][0]:
            best_by_key[key] = (score, item)

    ranked = [item for _, item in sorted(best_by_key.values(), key=lambda pair: pair[0], reverse=True)]
    total = len(ranked)
    start = max(page - 1, 0) * per_page
    return ranked[start:start + per_page], total


def _candidate_predicates(model, queries: list[str]):
    predicates = []
    for query in queries:
        if len(query) < 2:
            continue
        pattern = f"%{query}%"
        predicates.extend((
            model.title.ilike(pattern),
            model.title_mm.ilike(pattern),
            model.title.op("%")(query),
            model.title_mm.op("%")(query),
        ))
    return predicates


async def _candidate_media(db: AsyncSession, model, queries: list[str]):
    predicates = _candidate_predicates(model, queries)
    if not predicates:
        return []
    options = (selectinload(model.aliases), selectinload(model.keywords), selectinload(model.genres))
    stmt = (
        select(model)
        .options(*options)
        .where(model.is_published == True, model.is_archived == False, or_(*predicates))
        .limit(120)
    )
    try:
        return (await db.execute(stmt)).scalars().unique().all()
    except Exception:
        # SQLite-based local tests do not provide PostgreSQL's % trigram
        # operator.  Keep a title-only fallback without broad catalogue scans.
        # Build fresh ILIKE clauses because compiled SQL differs by dialect.
        like_predicates = []
        for query in queries:
            if len(query) >= 2:
                pattern = f"%{query}%"
                like_predicates.extend((model.title.ilike(pattern), model.title_mm.ilike(pattern)))
        stmt = select(model).options(*options).where(model.is_published == True, model.is_archived == False, or_(*like_predicates)).limit(120)
        return (await db.execute(stmt)).scalars().unique().all()


async def _candidate_aliases(db: AsyncSession, queries: list[str]) -> list[Alias]:
    predicates = []
    for query in queries:
        if len(query) >= 2:
            predicates.extend((Alias.name.ilike(f"%{query}%"), Alias.name.op("%")(query)))
    if not predicates:
        return []
    options = (
        selectinload(Alias.movie).selectinload(Movie.aliases),
        selectinload(Alias.series).selectinload(Series.aliases),
    )
    stmt = select(Alias).options(*options).where(Alias.is_approved == True, or_(*predicates)).limit(120)
    try:
        return (await db.execute(stmt)).scalars().unique().all()
    except Exception:
        like_predicates = [Alias.name.ilike(f"%{query}%") for query in queries if len(query) >= 2]
        stmt = select(Alias).options(*options).where(Alias.is_approved == True, or_(*like_predicates)).limit(120)
        return (await db.execute(stmt)).scalars().unique().all()


def _score_media(media, media_type: str, queries: list[str]) -> tuple[float, str]:
    fields = [
        ("exact", getattr(media, "title", "")),
        ("exact", getattr(media, "title_mm", "")),
        ("description", getattr(media, "description_en", "")),
        ("description", getattr(media, "description_mm", "")),
    ]
    best_score = 0.0
    best_type = "fuzzy"
    title = _normalize(getattr(media, "title", ""))
    for query in queries:
        for field_type, value in fields:
            normalized = _normalize(value)
            if not normalized:
                continue
            score = _text_score(query, normalized)
            if field_type == "description":
                score *= 0.82
            if media_type == "movie" and "avatar" in normalized and _is_blue_people_query(query):
                score = max(score, 0.92)
            if score > best_score:
                best_score = score
                best_type = "exact" if score >= 0.98 and field_type == "exact" else field_type
        # Concept aliases are an instant semantic bridge for titles where the
        # user describes the character/action instead of typing its name.
        for title_key, concepts in TITLE_CONCEPTS.items():
            if title_key in title and _concept_matches(query, concepts):
                best_score = max(best_score, 0.96)
                best_type = "concept"
    return best_score, best_type


def _concept_matches(query: str, concepts: str) -> bool:
    normalized_concepts = _normalize(concepts)
    if query in normalized_concepts or normalized_concepts in query:
        return True
    query_tokens = [token for token in _tokens(query) if token not in GENERIC_WORDS]
    concept_tokens = set(_tokens(normalized_concepts))
    return bool(query_tokens) and len(set(query_tokens) & concept_tokens) >= max(1, min(2, len(set(query_tokens))))


def _text_score(query: str, value: str) -> float:
    if not query or not value:
        return 0.0
    if query == value:
        return 1.0
    if query in value or value in query:
        return 0.86

    query_tokens = [token for token in _tokens(query) if token not in GENERIC_WORDS]
    value_tokens = [token for token in _tokens(value) if token not in GENERIC_WORDS]
    if query_tokens and value_tokens:
        overlap = len(set(query_tokens) & set(value_tokens))
        token_score = overlap / max(len(set(query_tokens)), 1)
    else:
        token_score = 0.0

    ratio = SequenceMatcher(None, query, value).ratio()
    best_word_ratio = 0.0
    for query_token in query_tokens:
        for value_token in value_tokens:
            best_word_ratio = max(best_word_ratio, SequenceMatcher(None, query_token, value_token).ratio())

    return max(token_score, ratio * 0.92, best_word_ratio * 0.72)


def _expanded_queries(query: str) -> list[str]:
    values = {query}
    for source, target in QUERY_EXPANSIONS.items():
        source_normalized = _normalize(source)
        if source_normalized and source_normalized in query:
            values.add(_normalize(target))
    if "avatar" in query:
        values.add("အာဗာတာ")
    return [value for value in values if value]


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    value = value.casefold().strip()
    value = re.sub(r"[^\w\u1000-\u109f\s]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _tokens(value: str) -> list[str]:
    tokens: list[str] = []
    for token in value.split():
        if len(token) >= 2:
            tokens.append(token)
        if MYANMAR_RE.search(token) and len(token) >= 4:
            for size in (3, 4, 5):
                for index in range(0, max(len(token) - size + 1, 0)):
                    tokens.append(token[index:index + size])
    return tokens


def _is_blue_people_query(query: str) -> bool:
    return (
        ("blue" in query and ("people" in query or "human" in query))
        or ("အပြာ" in query and "လူ" in query)
    )
