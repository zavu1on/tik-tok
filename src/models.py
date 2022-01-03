import ormar
from src.db import metadata, database


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Video(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'videos'

    id: int = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    title: str = ormar.String(nullable=False, max_length=100)
    likes: int = ormar.Integer(default=0)
    video_path: str = ormar.Text(nullable=False)


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'users'

    id: int = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    username: str = ormar.String(max_length=100, nullable=False)
    password: str = ormar.String(max_length=500, nullable=False)
    videos: list[Video] | None = ormar.ManyToMany(Video)


class Comment(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'comments'

    id: int = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    text: int = ormar.Text(nullable=False)
    video: Video = ormar.ForeignKey(Video)
    user: User = ormar.ForeignKey(User)
