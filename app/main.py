import asyncio

import uvicorn
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import insert, select

import auth
from api.router import api_router
from auth.router import auth_router
from modules.manager_modules import module_manager
from mysql.database import async_session_maker
from mysql.models import User
from pages.router import page_router
from settings import Settings
from websocket.ws_server import ws_router

app = FastAPI(title="TestTTK")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ws_router)
app.include_router(page_router)

origins = ["http://localhost", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

settings = Settings()
password_hasher = PasswordHasher()


@app.get("/")
async def root():
    return RedirectResponse(url="/pages/chat")


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
                email=settings.LOGIN,
            )
            await session.execute(stmt)
            await session.commit()

    asyncio.create_task(monitor_modules(module_manager))


async def monitor_modules(manager):
    while True:
        manager.manage_modules()
        await asyncio.sleep(10)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.WS_HOST,
        port=settings.WS_PORT,
        reload=True,
    )
