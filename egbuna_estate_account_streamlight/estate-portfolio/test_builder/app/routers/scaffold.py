import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models import TestCase
from app.deps import require_auth
from app.scaffold import test_id_to_path, generate_test_stub

router = APIRouter(prefix="/api/test-cases", tags=["scaffold"], dependencies=[Depends(require_auth)])


def _get_repo_tests_path():
    return os.environ.get("REPO_TESTS_PATH", "/repo/tests")


@router.post("/{test_id}/scaffold")
async def generate_scaffold(test_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    """Generate folder structure and pytest stub for a test case. Warns if file exists."""
    # Verify test case exists
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail=f"Test case {test_id} not found")

    repo_path = _get_repo_tests_path()
    try:
        test_file, test_dir = test_id_to_path(test_id, repo_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check if file already exists
    if os.path.exists(test_file):
        return JSONResponse(content={
            "warning": "File already exists - overwrite?",
            "path": test_file,
            "exists": True,
        })

    # Create directory and write file
    try:
        os.makedirs(test_dir, exist_ok=True)
        content = generate_test_stub(
            test_id=test_id,
            domain_code=tc.domain_code,
            workflow=tc.workflow,
            layer=tc.layer,
            test_type=tc.test_type,
            title=tc.title,
            requirement_ref=tc.requirement_ref,
        )
        with open(test_file, "w") as f:
            f.write(content)

        return JSONResponse(content={
            "message": "Scaffold generated",
            "path": test_file,
            "exists": False,
        })
    except PermissionError:
        raise HTTPException(status_code=500, detail=f"Cannot write to {REPO_TESTS_PATH} - check volume permissions")
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{test_id}/scaffold/overwrite")
async def overwrite_scaffold(test_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    """Explicitly overwrite an existing scaffold file."""
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail=f"Test case {test_id} not found")

    repo_path = _get_repo_tests_path()
    try:
        test_file, test_dir = test_id_to_path(test_id, repo_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        os.makedirs(test_dir, exist_ok=True)
        content = generate_test_stub(
            test_id=test_id,
            domain_code=tc.domain_code,
            workflow=tc.workflow,
            layer=tc.layer,
            test_type=tc.test_type,
            title=tc.title,
            requirement_ref=tc.requirement_ref,
        )
        with open(test_file, "w") as f:
            f.write(content)
        return JSONResponse(content={"message": "Scaffold overwritten", "path": test_file})
    except (PermissionError, OSError) as e:
        raise HTTPException(status_code=500, detail=str(e))
