from backend.models.user import User
from backend.models.movie import Movie
from backend.models.series import Series
from backend.models.episode import Episode
from backend.models.video import Video
from backend.models.genre import Genre, movie_genres, series_genres
from backend.models.keyword import Keyword, movie_keywords, series_keywords
from backend.models.alias import Alias
from backend.models.favorite import Favorite
from backend.models.watch_history import WatchHistory
from backend.models.report import Report
from backend.models.poll import Poll, PollOption, Vote
from backend.models.broadcast import Broadcast
from backend.models.advertisement import Advertisement
from backend.models.setting import Setting
from backend.models.language import Language
from backend.database import Base
# Note: Pydantic schemas are imported directly from backend.schemas when needed
