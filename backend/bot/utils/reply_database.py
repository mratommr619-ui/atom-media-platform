import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "reply_database.jsonl"


@dataclass(frozen=True)
class ReplyMatch:
    answer: str
    score: float


class ReplyDatabase:
    def __init__(self, path: Path = DATA_PATH):
        self.path = path
        self._loaded = False
        self._entries: list[dict] = []
        self._exact: dict[tuple[str, str], str] = {}
        self._index: dict[tuple[str, str], set[int]] = {}

    def find(self, text: str, lang: str) -> ReplyMatch | None:
        self._load()
        normalized = _normalize(text)
        if not normalized:
            return None

        exact = self._exact.get((lang, normalized)) or self._exact.get(("en", normalized))
        if exact:
            return ReplyMatch(answer=exact, score=1.0)

        tokens = list(_tokens(normalized))
        if not tokens:
            return None

        candidate_ids: set[int] = set()
        for token in tokens[:8]:
            candidate_ids.update(self._index.get((lang, token), set()))
        if not candidate_ids and lang != "en":
            for token in tokens[:8]:
                candidate_ids.update(self._index.get(("en", token), set()))
        if not candidate_ids:
            return None

        best_entry = None
        best_score = 0.0
        query_token_set = set(tokens)
        for entry_id in list(candidate_ids)[:250]:
            entry = self._entries[entry_id]
            entry_tokens = set(entry["tokens"])
            overlap = len(query_token_set & entry_tokens)
            if overlap == 0:
                continue
            score = overlap / max(len(query_token_set), len(entry_tokens), 1)
            if normalized in entry["query"] or entry["query"] in normalized:
                score += 0.35
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score >= 0.34:
            return ReplyMatch(answer=best_entry["answer"], score=best_score)
        return None

    def _load(self) -> None:
        if self._loaded:
            return
        if not self.path.exists():
            self._loaded = True
            return

        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw = json.loads(line)
                lang = raw.get("lang") or "en"
                answer = raw.get("answer") or ""
                for query in raw.get("queries", []):
                    normalized = _normalize(query)
                    if not normalized:
                        continue
                    entry_id = len(self._entries)
                    tokens = list(_tokens(normalized))
                    self._entries.append({
                        "lang": lang,
                        "query": normalized,
                        "tokens": tokens,
                        "answer": answer,
                    })
                    self._exact.setdefault((lang, normalized), answer)
                    for token in tokens:
                        self._index.setdefault((lang, token), set()).add(entry_id)
        self._loaded = True


def _normalize(value: str) -> str:
    value = value.casefold().strip()
    value = re.sub(r"[^\w\u1000-\u109f\s]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _tokens(value: str) -> Iterable[str]:
    for token in value.split():
        if len(token) >= 2:
            yield token
        if re.search(r"[\u1000-\u109f]", token) and len(token) >= 4:
            for size in (3, 4):
                for index in range(0, max(len(token) - size + 1, 0)):
                    yield token[index:index + size]


reply_database = ReplyDatabase()
