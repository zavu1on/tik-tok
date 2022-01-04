import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
from fastapi import APIRouter, HTTPException
from ormar import NoMatch
from src.schemas import RegistrationSchema, UpdateAccessTokenSchema
from src.models import User
from src.services import get_hashed_password, authenticate
from src.settings import KEY, ALGORITHM

auth = APIRouter()


@auth.post('/login/')
async def login(body: RegistrationSchema):
    try:
        user = await User.objects.filter(username=body.username, password=get_hashed_password(body.password)).first()

        return {'username': user.username, **authenticate(user)}
    except NoMatch:
        raise HTTPException(401, 'No matches in users!')


@auth.post('/registration/')
async def registration(body: RegistrationSchema):
    if len(body.username) > 100:
        raise HTTPException(400, 'Username should be less than 100 characters!')

    try:
        user = await User.objects.create(
            username=body.username,
            password=get_hashed_password(body.password)
        )

        return authenticate(user)

    except Exception as e:
        raise HTTPException(500, str(e))


@auth.post('/update-access-token/')
async def update_access_token(body: UpdateAccessTokenSchema):
    try:
        data = jwt.decode(body.refresh_token, KEY, ALGORITHM, {'verify_exp': True, 'verify_signature': True})

        user = await User.objects.filter(id=data['id']).first()

        return authenticate(user)

    except ExpiredSignatureError:
        raise HTTPException(403, 'Refresh token expired, login required!')
    except InvalidSignatureError:
        raise HTTPException(403, 'Invalid signature of token!')
    except NoMatch:
        raise HTTPException(403, 'No matches in users!')
    except DecodeError:
        raise HTTPException(403, 'Can not decode token!')
