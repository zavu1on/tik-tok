import jwt
from datetime import datetime, timedelta, timezone
from hashlib import md5
from typing import Callable, TypeVar, Generic

from fastapi import HTTPException

from src.models import User
from src.settings import KEY, ALGORITHM, TOKEN_PREFIX

T = TypeVar('T')


class MagicFunctions(Generic[T]):

    def __init__(self, *funcs: Callable):
        self.funcs = funcs

    def __ror__(self, iterable: T) -> T: ...


class filter(MagicFunctions):

    def __init__(self, *funcs):
        super().__init__(*funcs)

    def __ror__(self, iterable):
        res = []

        for i in iterable:
            flag = True
            for func in self.funcs:
                if not func(i):
                    flag = False

            if flag:
                res.append(i)

        return res


class map(MagicFunctions):
    def __init__(self, *funcs):
        super().__init__(*funcs)

    def __ror__(self, iterable):
        res = []

        for i in iterable:
            for func in self.funcs:
                i = func(i)
            res.append(i)

        return res


class find(MagicFunctions):
    def __init__(self, *funcs):
        super().__init__(*funcs)

    def __ror__(self, iterable):

        for i in iterable:
            flag = True
            for func in self.funcs:
                if not func(i):
                    flag = False

            if flag:
                return i


def get_hashed_password(password: str) -> str:
    return md5(password.encode('utf8')).hexdigest()


def authenticate(user: User) -> dict:

    access_token = jwt.encode(
        {
            'id': user.id,
            'type': 'access',
            'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=30),
        },
        KEY,
        algorithm=ALGORITHM
    )
    refresh_token = jwt.encode(
        {
            'id': user.id,
            'type': 'refresh',
            'exp': datetime.now(tz=timezone.utc) + timedelta(weeks=1)
        },
        KEY,
        algorithm=ALGORITHM
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def get_id_from_token(token: str) -> int:
    data = jwt.decode(token.split(TOKEN_PREFIX)[1], KEY, ALGORITHM, {'verify_exp': False, 'verify_signature': False})
    if data['type'] == 'refresh':
        raise HTTPException(400, 'Access token expected!')
    return int(data['id'])


def parse_videos_to_json(video) -> dict:
    return {
        'id': video.id,
        'likes': video.likes,
        'video_path': video.video_path,
        'users': video.users | map(lambda x: {'id': x.id, 'username': x.username}),
        'comments': video.comments | map(lambda x: {'id': x.id, 'text': x.text})
    }
