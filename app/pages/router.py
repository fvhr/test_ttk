from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import auth
from mysql.database import get_async_session
from mysql.models import User
from pages import settings

page_router = APIRouter(
    prefix="/pages",
    tags=["Pages"]
)

templates = Jinja2Templates(directory="templates")


@page_router.get("/chat")
def get_chat_page(request: Request):
    return templates.TemplateResponse("get_token.html", {"request": request})


@page_router.post("/chat")
def redirect_with_token(token: str = Form(...)):
    return RedirectResponse(url=f"/pages/chat/{token}", status_code=303)


@page_router.get("/chat/{token}")
def get_chat_page_with_token(request: Request, token: str):
    if token == settings.WS_TOKEN:
        return templates.TemplateResponse("chat.html", {"request": request, "token": token})
    return templates.TemplateResponse("get_token.html",
                                      {"request": request, "message": "Invalid token", "token": token})


@page_router.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Обработка формы авторизации
@page_router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_async_session), username: str = Form(...),
                password: str = Form(...)):
    stmt = select(User).where(User.email == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not auth.utils.verify(password, user.hashed_password):
        return {"message": "Invalid Credentials"}, 401  # Return a JSON response with status 401

    access_token = auth.oauth2.create_access_token(data={"user_id": str(user.id)})
    print(access_token)
    return {"access_token": access_token}  # Return the token in the response body


@page_router.get("/api")
async def get_api_page(request: Request):
    return templates.TemplateResponse("api.html", {"request": request})
