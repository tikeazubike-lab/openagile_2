import datetime
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_session
from app.models import TestCase, TestRun, Report, BugReport
from app.deps import require_auth
from app.templates_module import templates

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def reports_page(request: Request, session: AsyncSession = Depends(get_session)):
    """List all generated reports."""
    result = await session.execute(select(Report).order_by(Report.generated_at.desc()))
    reports = result.scalars().all()

    # Also get bug reports
    bug_result = await session.execute(select(BugReport).order_by(BugReport.generated_at.desc()))
    bug_reports = bug_result.scalars().all()

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "reports": [{"id": r.id, "generated_at": r.generated_at.isoformat() if r.generated_at else ""} for r in reports],
        "bug_reports": [{"id": b.id, "test_run_id": b.test_run_id, "generated_at": b.generated_at.isoformat() if b.generated_at else ""} for b in bug_reports],
    })


@router.post("/api/submit")
async def submit_report(session: AsyncSession = Depends(get_session)):
    """Generate a markdown report from the latest run of each test case."""
    # Check all test cases have at least one run
    tc_count = await session.execute(select(func.count(TestCase.id)))
    total_cases = tc_count.scalar()

    cases_with_runs = await session.execute(
        select(func.count(func.distinct(TestRun.test_case_id)))
    )
    runs_count = cases_with_runs.scalar()

    if total_cases == 0:
        raise HTTPException(status_code=400, detail="No test cases exist yet")
    if total_cases != runs_count:
        raise HTTPException(status_code=400, detail="All test cases must have at least one execution result")

    # Build markdown report
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Test Run Report — {now}", "", "| Test ID | Status | Expected | Actual |", "|---|---|---|---|"]

    result = await session.execute(select(TestCase).order_by(TestCase.id))
    test_cases = result.scalars().all()

    for tc in test_cases:
        latest = await session.execute(
            select(TestRun).where(TestRun.test_case_id == tc.id).order_by(TestRun.run_number.desc()).limit(1)
        )
        run = latest.scalar_one_or_none()
        if run:
            lines.append(f"| {tc.id} | {run.status} | {run.expected_result} | {run.actual_result} |")

    markdown = "\n".join(lines)

    report = Report(markdown=markdown)
    session.add(report)
    await session.commit()

    return JSONResponse(content={"report_id": report.id, "markdown": markdown})


@router.get("/api/reports/{report_id}/download")
async def download_report(report_id: int, session: AsyncSession = Depends(get_session)):
    """Download a saved report as .md file."""
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"test-report-{report_id}_{now}.md"
    return PlainTextResponse(
        content=report.markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/api/bug-reports/{bug_report_id}/download")
async def download_bug_report(bug_report_id: int, session: AsyncSession = Depends(get_session)):
    """Download a bug report as .md file."""
    result = await session.execute(select(BugReport).where(BugReport.id == bug_report_id))
    bug = result.scalar_one_or_none()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
    return PlainTextResponse(
        content=bug.markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=bug-report-{bug_report_id}.md"},
    )
