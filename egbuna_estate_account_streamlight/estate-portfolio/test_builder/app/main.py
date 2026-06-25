import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
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

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(test_cases.router)
app.include_router(test_runs.router)
app.include_router(reports.router)
app.include_router(domain_codes.router)
app.include_router(scaffold.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/test-cases")
