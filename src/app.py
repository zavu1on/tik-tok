import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, DecodeError
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.routes.api import api
from src.settings import TOKEN_PREFIX, KEY, ALGORITHM, AUTH_REQUIRED_URLS, VIDEO_PACK_SIZE
from src.db import database, metadata, engine
from src.routes.auth import auth
from src.services import filter, map, parse_videos_to_json
from src.models import User, Video, Comment

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.database = database
metadata.create_all(engine)
app.include_router(auth, prefix='/auth')
app.include_router(api, prefix='/api')


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.middleware('http')
async def auth_required(request: Request, call_next):
    if request.url.path in AUTH_REQUIRED_URLS:

        try:
            authorization = request.headers['authorization']
            token = authorization.split(TOKEN_PREFIX)[1]

            jwt.decode(token, KEY, ALGORITHM, {'verify_exp': True, 'verify_signature': True})
            response = await call_next(request)

            return response

        except ExpiredSignatureError:
            return JSONResponse({'detail': 'Access token expired, refresh it!'}, 403)
        except InvalidSignatureError:
            return JSONResponse({'detail': 'Invalid signature of token!'}, 403)
        except (IndexError, KeyError):
            return JSONResponse({'detail': 'Access token is required!'}, 403)
        except DecodeError:
            return JSONResponse({'detail': 'Can not decode token!'}, 403)

    response = await call_next(request)
    return response


@app.websocket('/get-videos/')
async def get_videos(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_json()  # {'last_video_id': int}
        last_video_id = data['last_video_id']

        if 'last_video_id' not in data:
            await websocket.send_json({
                'success': False,
                'detail': 'Invalid data format!'
            })
        else:
            videos = await Video.objects.select_related('users').select_related('comments').all() \
                     | filter(lambda v: last_video_id < v.id < last_video_id + VIDEO_PACK_SIZE) \
                     | map(parse_videos_to_json)

            await websocket.send_json({
                'success': True,
                'data': videos
            })

