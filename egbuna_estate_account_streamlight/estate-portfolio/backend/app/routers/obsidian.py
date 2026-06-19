from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_session, require_admin
from app.models import ObsidianSyncLog
from pydantic import BaseModel
import subprocess
import os

router = APIRouter(prefix="/api/v1/obsidian", tags=["Obsidian"])

class ImportRequest(BaseModel):
    vault_path: str
    dry_run: bool = False

def run_import_script(vault_path: str, dry_run: bool):
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts", "import_obsidian.py")
    cmd = ["python", script_path, "--vault-path", vault_path]
    if dry_run:
        cmd.append("--dry-run")
    
    env = os.environ.copy()
    # ensure PYTHONPATH is set so that app modules can be imported
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    subprocess.run(cmd, env=env)

@router.post("/import")
async def trigger_import(req: ImportRequest, background_tasks: BackgroundTasks, current_user = Depends(require_admin)):
    background_tasks.add_task(run_import_script, req.vault_path, req.dry_run)
    return {"message": "Import started in background"}

@router.get("/sync-log")
async def get_sync_log(session: AsyncSession = Depends(get_session), current_user = Depends(require_admin)):
    result = await session.execute(select(ObsidianSyncLog).order_by(ObsidianSyncLog.run_at.desc()))
    return result.scalars().all()
