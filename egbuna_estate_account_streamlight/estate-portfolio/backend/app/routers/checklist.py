import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session, require_admin
from app.models import ChecklistRun, User

router = APIRouter(prefix="/api/v1/checklist", tags=["checklist"])


class SaveRunRequest(BaseModel):
    results: dict
    signoff_markdown: str


@router.get("/runs")
async def list_runs(
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            ChecklistRun.id,
            ChecklistRun.admin_id,
            ChecklistRun.results_json,
            ChecklistRun.created_at,
            User.username,
        )
        .join(User, ChecklistRun.admin_id == User.id)
        .where(User.deleted_at.is_(None))
        .order_by(desc(ChecklistRun.created_at))
        .limit(10)
    )
    result = await session.execute(stmt)
    rows = result.all()

    data = []
    for row in rows:
        results = row.results_json
        pass_count = sum(1 for v in results.values() if v is True)
        fail_count = sum(1 for v in results.values() if v is False)
        skip_count = sum(1 for v in results.values() if v is None)
        data.append({
            "id": row.id,
            "username": row.username,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "skip_count": skip_count,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        })

    return {"data": data, "meta": {"total": len(data)}}


@router.post("/runs", status_code=201)
async def save_run(
    body: SaveRunRequest,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    run = ChecklistRun(
        admin_id=admin.id,
        results_json=body.results,
        signoff_markdown=body.signoff_markdown,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    return {
        "data": {
            "id": run.id,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        }
    }


@router.get("/test-checklist", include_in_schema=False)
async def test_checklist_page(
    admin: User = Depends(require_admin),
):
    path = os.path.join(os.path.dirname(__file__), "..", "static", "checklist", "index.html")
    from fastapi.responses import FileResponse
    return FileResponse(path)