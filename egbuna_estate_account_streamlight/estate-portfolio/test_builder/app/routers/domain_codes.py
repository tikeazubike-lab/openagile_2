from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models import DomainCode
from app.deps import require_auth
from app.templates_module import templates

router = APIRouter(prefix="/admin/domain-codes", tags=["domain-codes"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def list_domain_codes(request: Request, session: AsyncSession = Depends(get_session)):
    """List all domain codes with add/edit forms."""
    result = await session.execute(select(DomainCode).order_by(DomainCode.code))
    codes = result.scalars().all()
    return templates.TemplateResponse("admin_domain_codes.html", {
        "request": request,
        "codes": [{"code": c.code, "label": c.label, "folder_slug": c.folder_slug} for c in codes],
    })


@router.post("")
async def add_domain_code(
    request: Request,
    session: AsyncSession = Depends(get_session),
    code: str = Form(...),
    label: str = Form(...),
    folder_slug: str = Form(...),
):
    """Add a new domain code. Reject duplicates."""
    code = code.upper().strip()
    label = label.strip()
    folder_slug = folder_slug.strip()

    if not code or not label or not folder_slug:
        raise HTTPException(status_code=400, detail="All fields are required")

    if len(code) > 4:
        raise HTTPException(status_code=400, detail="Domain code must be 4 characters or less")

    # Check duplicate
    existing = await session.execute(select(DomainCode).where(DomainCode.code == code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Domain code {code} already exists")

    dc = DomainCode(code=code, label=label, folder_slug=folder_slug)
    session.add(dc)
    await session.commit()
    return RedirectResponse(url="/admin/domain-codes", status_code=302)


@router.post("/{code}/edit")
async def edit_domain_code(
    code: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    label: str = Form(...),
    folder_slug: str = Form(...),
):
    """Edit an existing domain code label and folder slug."""
    result = await session.execute(select(DomainCode).where(DomainCode.code == code.upper()))
    dc = result.scalar_one_or_none()
    if not dc:
        raise HTTPException(status_code=404, detail="Domain code not found")

    dc.label = label.strip()
    dc.folder_slug = folder_slug.strip()
    await session.commit()
    return RedirectResponse(url="/admin/domain-codes", status_code=302)


@router.post("/{code}/delete")
async def delete_domain_code(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete a domain code."""
    result = await session.execute(select(DomainCode).where(DomainCode.code == code.upper()))
    dc = result.scalar_one_or_none()
    if not dc:
        raise HTTPException(status_code=404, detail="Domain code not found")

    # Check if any test cases use this domain
    from app.models import TestCase
    tc_check = await session.execute(select(TestCase).where(TestCase.domain_code == code.upper()))
    if tc_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Cannot delete {code}: test cases exist for this domain")

    await session.delete(dc)
    await session.commit()
    return RedirectResponse(url="/admin/domain-codes", status_code=302)
