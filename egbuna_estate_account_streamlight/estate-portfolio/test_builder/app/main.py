import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.templates_module import templates
from app.routers import auth, test_cases, test_runs, reports, domain_codes, scaffold


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="EPM Test Case Builder", lifespan=lifespan)


@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/login")
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(test_runs.router)
app.include_router(test_cases.router)
app.include_router(reports.router)
app.include_router(domain_codes.router)
app.include_router(scaffold.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/test-cases")
