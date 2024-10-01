from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import insert, select

import auth
from api.router import api_router
from auth.router import auth_router
from mysql.database import async_session_maker
from mysql.models import User
from pages.router import chat_router
from settings import Settings
from websocket.ws_server import ws_router

app = FastAPI(
    title="TestTTK"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ws_router)
app.include_router(chat_router)

origins = [
    "http://localhost",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

settings = Settings()

password_hasher = PasswordHasher()


@app.on_event("startup")
async def startup_event():
    async with async_session_maker() as session:
        stmt = select(User).where(User.email == settings.LOGIN)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user is None:
            hashed_password = auth.utils.hash(settings.PASSWORD)
            stmt = insert(User).values(
                hashed_password=hashed_password,
                email=settings.LOGIN
            )
            await session.execute(stmt)
            await session.commit()
