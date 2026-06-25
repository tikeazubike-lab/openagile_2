from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.deps import create_session, SHARED_PASSWORD, require_auth
from app.templates_module import templates

router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password != SHARED_PASSWORD:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=401,
        )
    response = RedirectResponse(url="/test-cases", status_code=302)
    response.set_cookie(
        key="session",
        value=create_session(),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 12,  # 12 hours
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session", httponly=True, secure=True, samesite="lax")
    return response
