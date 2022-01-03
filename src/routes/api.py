import shutil
from datetime import datetime
from random import random
from fastapi import APIRouter, UploadFile, File, Body, Header, HTTPException
from ormar import NoMatch
from src.models import User, Video, Comment
from src.schemas import GetCommentsSchema, LikeVideoSchema, AddCommentSchema
from src.services import get_id_from_token

api = APIRouter()


@api.get('/get-comments/')
async def get_comments(body: GetCommentsSchema):
    comments = await Comment.objects.filter(video__id=body.video_id).all()

    return comments


@api.post('/add-video/')
async def add_video(title: str = Body(...), video: UploadFile = File(...), authorization: str = Header('')):

    path = f'static/media/{str(datetime.now().timestamp()).replace(".", "_")}.{str(random()).replace(".", "")}.mp4'
    _id = get_id_from_token(authorization)

    with open(f'./{path}', 'wb') as buffer:
        shutil.copyfileobj(video.file, buffer)

    v = await Video.objects.create(title=title, video_path=f'/{path}')
    u = await User.objects.filter(id=_id).first()
    await u.videos.add(v)
    await u.update()

    return {}


@api.post('/like-video/')
async def like_video(body: LikeVideoSchema):
    try:
        video = await Video.objects.filter(id=body.video_id).first()
        video.likes += 1

        await video.update()
        return {}
    except NoMatch:
        raise HTTPException(404, 'Can not find video!')


@api.post('/add-comment/')
async def add_comment(body: AddCommentSchema, authorization: str = Header('')):
    try:
        v = await Video.objects.filter(id=body.video_id).first()
        u = await User.objects.filter(id=get_id_from_token(authorization)).first()

        await Comment.objects.create(
            text=body.text,
            video=v,
            user=u
        )

        return {}
    except NoMatch:
        raise HTTPException(404, 'Can not find or user video!')
