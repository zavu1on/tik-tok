from pydantic import BaseModel


class RegistrationSchema(BaseModel):
    username: str
    password: str


class UpdateAccessTokenSchema(BaseModel):
    refresh_token: str


class GetCommentsSchema(BaseModel):
    video_id: int


class LikeVideoSchema(BaseModel):
    video_id: int


class AddCommentSchema(BaseModel):
    video_id: int
    text: str
