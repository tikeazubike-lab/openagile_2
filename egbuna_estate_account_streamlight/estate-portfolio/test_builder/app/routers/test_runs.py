from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_session
from app.models import TestCase, TestRun, BugReport
from app.deps import require_auth
from app.templates_module import templates

router = APIRouter(prefix="/test-cases/execute", tags=["test-runs"], dependencies=[Depends(require_auth)])


def _generate_bug_report(run, test_case):
    """Generate bug report markdown from EPM template."""
    lines = [
        f"# Bug Report — {test_case.id}",
        "",
        "## What I Did",
        run.execution_path,
        "",
        "## What I Expected",
        run.expected_result,
        "",
        "## What Actually Happened",
        run.actual_result,
        "",
        "## Feature Affected",
        test_case.domain_code,
        "",
        "## Severity",
        "(leave blank)",
        "",
        "## Layer",
        test_case.layer,
        "",
        "## Evidence",
        "(leave blank)",
        "",
        "## Agent Instructions",
        "",
        "Steps to reproduce:",
        "1. " + run.execution_path,
        "",
        "Expected result: " + run.expected_result,
        "",
        "Actual result: " + run.actual_result,
    ]
    return "\n".join(lines)


@router.get("", response_class=HTMLResponse)
async def execute_page(request: Request, session: AsyncSession = Depends(get_session)):
    """Render the Execute Tests page with all test cases and their latest run."""
    result = await session.execute(select(TestCase).order_by(TestCase.id))
    test_cases = result.scalars().all()

    cases_with_runs = []
    for tc in test_cases:
        latest_result = await session.execute(
            select(TestRun).where(TestRun.test_case_id == tc.id).order_by(TestRun.run_number.desc()).limit(1)
        )
        latest_run = latest_result.scalar_one_or_none()

        # Get all runs for history
        all_runs_result = await session.execute(
            select(TestRun).where(TestRun.test_case_id == tc.id).order_by(TestRun.run_number)
        )
        all_runs = all_runs_result.scalars().all()

        run_history = []
        for r in all_runs:
            run_history.append({
                "run_number": r.run_number,
                "status": r.status,
                "executed_at": r.executed_at.isoformat() if r.executed_at else "",
            })

        cases_with_runs.append({
            "test_case": {
                "id": tc.id,
                "title": tc.title,
                "domain_code": tc.domain_code,
                "workflow": tc.workflow,
                "layer": tc.layer,
                "test_type": tc.test_type,
                "tags": tc.tags,
            },
            "latest_run": {
                "run_number": latest_run.run_number if latest_run else None,
                "status": latest_run.status if latest_run else None,
                "executed_at": latest_run.executed_at.isoformat() if latest_run and latest_run.executed_at else None,
            } if latest_run else None,
            "run_history": run_history,
            "total_runs": len(all_runs),
        })

    return templates.TemplateResponse("execute.html", {
        "request": request,
        "test_cases": cases_with_runs,
    })


@router.post("/api/runs")
async def save_run(request: Request, session: AsyncSession = Depends(get_session)):
    """Save a test run. If status=Failed, auto-generate a bug report."""
    body = await request.json()
    test_case_id = body.get("test_case_id")
    execution_path = body.get("execution_path", "")
    expected_result = body.get("expected_result", "")
    actual_result = body.get("actual_result", "")
    status = body.get("status", "")

    # Validation
    if not actual_result:
        raise HTTPException(status_code=400, detail="Actual result is required")
    if status not in ("Passed", "Failed"):
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    # Verify test case exists
    tc_result = await session.execute(select(TestCase).where(TestCase.id == test_case_id))
    tc = tc_result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail=f"Test case {test_case_id} not found")

    # Get next run number
    result = await session.execute(
        select(func.coalesce(func.max(TestRun.run_number), 0))
        .where(TestRun.test_case_id == test_case_id)
    )
    run_number = result.scalar() + 1

    run = TestRun(
        test_case_id=test_case_id,
        run_number=run_number,
        execution_path=execution_path,
        expected_result=expected_result,
        actual_result=actual_result,
        status=status,
    )
    session.add(run)
    await session.flush()  # get run.id

    # Auto-generate bug report if Failed
    bug_report_id = None
    if status == "Failed":
        bug_markdown = _generate_bug_report(run, tc)
        bug_report = BugReport(test_run_id=run.id, markdown=bug_markdown)
        session.add(bug_report)
        await session.flush()
        bug_report_id = bug_report.id

    await session.commit()
    return JSONResponse(content={
        "run_id": run.id,
        "run_number": run_number,
        "status": status,
        "bug_report_id": bug_report_id,
    })
