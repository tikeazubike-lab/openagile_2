import json
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.database import get_session
from app.models import TestCase, DomainCode, TestRun
from app.deps import require_auth
from app.templates_module import templates

router = APIRouter(prefix="/test-cases", tags=["test-cases"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def add_test_cases_page(request: Request, session: AsyncSession = Depends(get_session)):
    """Render the Add Test Cases page with domain dropdown from DB."""
    result = await session.execute(select(DomainCode).order_by(DomainCode.code))
    domains = result.scalars().all()
    domain_list = []
    for d in domains:
        try:
            workflows = json.loads(d.workflows) if d.workflows else []
        except (json.JSONDecodeError, TypeError):
            workflows = []
        domain_list.append({
            "code": d.code,
            "label": d.label,
            "folder_slug": d.folder_slug,
            "workflows": workflows,
        })
    return templates.TemplateResponse("test_cases.html", {
        "request": request,
        "domains_json": json.dumps(domain_list),
        "domains": domain_list,
        "test_id_format": "DOMAIN-WORKFLOW-LAYER-TYPE-NNN",
    })


@router.post("/api/submit")
async def submit_test_cases(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Submit all drafted test cases from localStorage to the database."""
    body = await request.json()
    cases = body.get("cases", [])
    if not cases:
        raise HTTPException(status_code=400, detail="Add at least one test case before submitting")

    created = []
    for case in cases:
        # Validate required fields
        if not case.get("layer"):
            raise HTTPException(status_code=400, detail="Layer is required to generate a Test ID")
        if not case.get("domain"):
            raise HTTPException(status_code=400, detail="Domain is required to generate a Test ID")
        if not case.get("workflow"):
            raise HTTPException(status_code=400, detail="Workflow is required to generate a Test ID")
        if not case.get("test_type"):
            raise HTTPException(status_code=400, detail="Test type is required to generate a Test ID")
        if not case.get("title"):
            raise HTTPException(status_code=400, detail="Title is required")

        # Compute next sequence number
        result = await session.execute(
            select(func.coalesce(func.max(TestCase.sequence_no), 0))
            .where(
                TestCase.domain_code == case["domain"].upper(),
                TestCase.workflow == case["workflow"].upper(),
                TestCase.layer == case["layer"].upper(),
                TestCase.test_type == case["test_type"].upper(),
            )
        )
        seq = result.scalar() + 1

        test_id = f"{case['domain'].upper()}-{case['workflow'].upper()}-{case['layer'].upper()}-{case['test_type'].upper()}-{seq:03d}"

        # Check if this ID already exists (race condition protection)
        existing = await session.execute(
            select(TestCase.id).where(TestCase.id == test_id)
        )
        if existing.scalar_one_or_none():
            seq += 1
            test_id = f"{case['domain'].upper()}-{case['workflow'].upper()}-{case['layer'].upper()}-{case['test_type'].upper()}-{seq:03d}"

        tc = TestCase(
            id=test_id,
            domain_code=case["domain"].upper(),
            workflow=case["workflow"].upper(),
            layer=case["layer"].upper(),
            test_type=case["test_type"].upper(),
            sequence_no=seq,
            title=case.get("title", ""),
            requirement_ref=case.get("requirement_ref"),
            tags=",".join(case.get("tags", [])) if isinstance(case.get("tags"), list) else case.get("tags", ""),
        )
        session.add(tc)
        created.append(test_id)

    await session.commit()
    return JSONResponse(content={"submitted": created, "count": len(created)})


@router.get("/api/next-sequence")
async def get_next_sequence(
    domain: str,
    workflow: str,
    layer: str,
    test_type: str,
    session: AsyncSession = Depends(get_session),
):
    """Get the next sequence number for a taxonomy tuple (used by client for preview)."""
    result = await session.execute(
        select(func.coalesce(func.max(TestCase.sequence_no), 0))
        .where(
            TestCase.domain_code == domain.upper(),
            TestCase.workflow == workflow.upper(),
            TestCase.layer == layer.upper(),
            TestCase.test_type == test_type.upper(),
        )
    )
    max_seq = result.scalar()
    return JSONResponse(content={"sequence_no": max_seq + 1})


@router.get("/{test_id}")
async def get_test_case(test_id: str, session: AsyncSession = Depends(get_session)):
    """Get a single test case by ID."""
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    return JSONResponse(content={
        "id": tc.id,
        "domain_code": tc.domain_code,
        "workflow": tc.workflow,
        "layer": tc.layer,
        "test_type": tc.test_type,
        "sequence_no": tc.sequence_no,
        "title": tc.title,
        "requirement_ref": tc.requirement_ref,
    })


@router.put("/{test_id}")
async def update_test_case(
    test_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing test case (title and requirement_ref only)."""
    body = await request.json()
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    # Only allow updating title and requirement_ref
    if "title" in body:
        tc.title = body["title"]
    if "requirement_ref" in body:
        tc.requirement_ref = body["requirement_ref"]

    await session.commit()
    return JSONResponse(content={"id": tc.id, "title": tc.title, "requirement_ref": tc.requirement_ref})


@router.delete("/{test_id}")
async def delete_test_case(test_id: str, session: AsyncSession = Depends(get_session)):
    """Delete a test case — cascades to delete runs and bug reports."""
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    await session.delete(tc)
    await session.commit()
    return JSONResponse(content={"message": "Test case and associated runs deleted"})
