"""
EPM — Registrars router.
Phase 3B: Registrars document management.
"""

import os
from datetime import datetime, timezone
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.deps import get_current_user, require_admin, get_session
from app.models import User, Registrar, RegistrarContactField, RegistrarRequirement, RegistrarDocument, Company

router = APIRouter(tags=["Registrars"])

UPLOAD_BASE = "/app/uploads/registrar_documents"
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB


def _envelope(data: object) -> dict:
    return {"data": data, "meta": {}, "error": None}


class ContactFieldIn(BaseModel):
    field_type: Literal['phone', 'email', 'address', 'website', 'other']
    field_value: str
    label: Optional[str] = None
    sort_order: int = 0


class RegistrarCreateUpdate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None
    response_rating: int | None = None
    notes: str | None = None
    contact_fields: Optional[list[ContactFieldIn]] = None


class RequirementCreateUpdate(BaseModel):
    task_name: str
    document_title: str
    description: Optional[str] = None
    is_required: bool = True
    sort_order: int = 0


class DocumentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


# ─── Registrars ─────────────────────────────────────────────────────────────

@router.get("/registrars")
async def list_registrars(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Registrar).options(
        selectinload(Registrar.companies),
        selectinload(Registrar.contact_fields),
        selectinload(Registrar.requirements).selectinload(RegistrarRequirement.documents)
    ).where(Registrar.deleted_at.is_(None))
    
    result = await session.execute(stmt)
    registrars = result.scalars().all()
    
    response_data = []
    for r in registrars:
        linked_companies = [{"id": c.id, "ticker": c.ticker, "name": c.name} for c in r.companies if c.deleted_at is None]
        active_reqs = [req for req in r.requirements if req.deleted_at is None]
        
        pending_doc_count = 0
        for req in active_reqs:
            docs = [d for d in req.documents if d.deleted_at is None]
            if not docs:
                pending_doc_count += 1
                
        active_fields = [
            {
                "id": f.id,
                "field_type": f.field_type,
                "field_value": f.field_value,
                "label": f.label,
                "sort_order": f.sort_order
            }
            for f in r.contact_fields if f.deleted_at is None
        ]
        
        response_data.append({
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "phone": r.phone,
            "address": r.address,
            "website": r.website,
            "response_rating": r.response_rating,
            "notes": r.notes,
            "contact_fields": active_fields,
            "linked_company_count": len(linked_companies),
            "linked_companies": linked_companies,
            "requirement_count": len(active_reqs),
            "pending_document_count": pending_doc_count,
        })
        
    return _envelope(response_data)


@router.post("/registrars")
async def create_registrar(
    data: RegistrarCreateUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    registrar = Registrar(
        name=data.name,
        email=data.email,
        phone=data.phone,
        address=data.address,
        website=data.website,
        response_rating=data.response_rating,
        notes=data.notes,
        deleted_at=None
    )
    session.add(registrar)
    await session.commit()
    await session.refresh(registrar)
    return _envelope({"id": registrar.id, "name": registrar.name})


@router.get("/registrars/{id}")
async def get_registrar(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Registrar).options(
        selectinload(Registrar.companies),
        selectinload(Registrar.contact_fields),
        selectinload(Registrar.requirements).selectinload(RegistrarRequirement.documents)
    ).where(Registrar.id == id, Registrar.deleted_at.is_(None))
    
    result = await session.execute(stmt)
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Registrar not found")
        
    linked_companies = [{"id": c.id, "ticker": c.ticker, "name": c.name} for c in r.companies if c.deleted_at is None]
    active_reqs = [req for req in r.requirements if req.deleted_at is None]
    
    pending_doc_count = 0
    for req in active_reqs:
        docs = [d for d in req.documents if d.deleted_at is None]
        if not docs:
            pending_doc_count += 1
            
    active_fields = [
        {
            "id": f.id,
            "field_type": f.field_type,
            "field_value": f.field_value,
            "label": f.label,
            "sort_order": f.sort_order
        }
        for f in r.contact_fields if f.deleted_at is None
    ]
            
    return {"id": r.id,
        "name": r.name,
        "email": r.email,
        "phone": r.phone,
        "address": r.address,
        "website": r.website,
        "response_rating": r.response_rating,
        "notes": r.notes,
        "contact_fields": active_fields,
        "linked_company_count": len(linked_companies),
        "linked_companies": linked_companies,
        "requirement_count": len(active_reqs),
        "pending_document_count": pending_doc_count,
    }


@router.put("/registrars/{id}")
async def update_registrar(
    id: int,
    data: RegistrarCreateUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    registrar = await session.get(Registrar, id)
    if not registrar or registrar.deleted_at:
        raise HTTPException(404, "Registrar not found")
        
    registrar.name = data.name
    registrar.email = data.email
    registrar.phone = data.phone
    registrar.address = data.address
    registrar.website = data.website
    registrar.response_rating = data.response_rating
    registrar.notes = data.notes
    
    if data.contact_fields is not None:
        # Soft delete existing fields
        stmt = select(RegistrarContactField).where(
            RegistrarContactField.registrar_id == id,
            RegistrarContactField.deleted_at.is_(None)
        )
        result = await session.execute(stmt)
        existing_fields = result.scalars().all()
        now = datetime.now(timezone.utc)
        for field in existing_fields:
            field.deleted_at = now
            
        # Add new fields
        for f in data.contact_fields:
            new_field = RegistrarContactField(
                registrar_id=id,
                field_type=f.field_type,
                field_value=f.field_value,
                label=f.label,
                sort_order=f.sort_order
            )
            session.add(new_field)
    
    await session.commit()
    
    # Return the updated object
    stmt = select(RegistrarContactField).where(
        RegistrarContactField.registrar_id == id,
        RegistrarContactField.deleted_at.is_(None)
    )
    result = await session.execute(stmt)
    active_fields = [
        {
            "id": f.id,
            "field_type": f.field_type,
            "field_value": f.field_value,
            "label": f.label,
            "sort_order": f.sort_order
        }
        for f in result.scalars().all()
    ]
    
    return _envelope({
        "id": registrar.id, 
        "message": "Updated",
        "contact_fields": active_fields
    })


@router.delete("/registrars/{id}")
async def delete_registrar(
    id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    registrar = await session.get(Registrar, id)
    if not registrar or registrar.deleted_at:
        raise HTTPException(404, "Registrar not found")
        
    registrar.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return _envelope({"id": id, "message": "Deleted"})


# ─── Requirements ───────────────────────────────────────────────────────────

@router.get("/registrars/{id}/requirements")
async def list_requirements(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(RegistrarRequirement).options(
        selectinload(RegistrarRequirement.documents).selectinload(RegistrarDocument.company)
    ).where(
        RegistrarRequirement.registrar_id == id,
        RegistrarRequirement.deleted_at.is_(None)
    ).order_by(RegistrarRequirement.sort_order, RegistrarRequirement.id)
    
    result = await session.execute(stmt)
    requirements = result.scalars().all()
    
    response_data = []
    for req in requirements:
        docs = [d for d in req.documents if d.deleted_at is None]
        docs.sort(key=lambda x: x.uploaded_at, reverse=True)
        latest_doc = docs[0] if docs else None
        
        doc_data = None
        if latest_doc:
            doc_data = {
                "id": latest_doc.id,
                "file_name": latest_doc.file_name,
                "file_size": latest_doc.file_size,
                "status": latest_doc.status,
                "uploaded_at": latest_doc.uploaded_at.isoformat(),
                "company_ticker": latest_doc.company.ticker if latest_doc.company else None
            }
            
        response_data.append({
            "id": req.id,
            "task_name": req.task_name,
            "document_title": req.document_title,
            "description": req.description,
            "is_required": req.is_required,
            "sort_order": req.sort_order,
            "latest_document": doc_data,
            "document_count": len(docs)
        })
        
    return _envelope(response_data)


@router.post("/registrars/{id}/requirements")
async def create_requirement(
    id: int,
    data: RequirementCreateUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    req = RegistrarRequirement(
        registrar_id=id,
        task_name=data.task_name,
        document_title=data.document_title,
        description=data.description,
        is_required=data.is_required,
        sort_order=data.sort_order
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)
    return _envelope({"id": req.id})


@router.put("/registrar-requirements/{id}")
async def update_requirement(
    id: int,
    data: RequirementCreateUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    req = await session.get(RegistrarRequirement, id)
    if not req or req.deleted_at:
        raise HTTPException(404, "Requirement not found")
        
    req.task_name = data.task_name
    req.document_title = data.document_title
    req.description = data.description
    req.is_required = data.is_required
    req.sort_order = data.sort_order
    
    await session.commit()
    return _envelope({"id": req.id, "message": "Updated"})


@router.delete("/registrar-requirements/{id}")
async def delete_requirement(
    id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    req = await session.get(RegistrarRequirement, id)
    if not req or req.deleted_at:
        raise HTTPException(404, "Requirement not found")
        
    req.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return _envelope({"id": id, "message": "Deleted"})


# ─── Documents ──────────────────────────────────────────────────────────────

@router.post("/registrar-requirements/{req_id}/documents")
async def upload_document(
    req_id: int,
    file: UploadFile = File(...),
    company_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    req = await session.get(RegistrarRequirement, req_id)
    if not req or req.deleted_at:
        raise HTTPException(404, "Requirement not found")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(422, "File type not allowed. Accepted: PDF, JPG, PNG")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(422, "File exceeds 20MB limit")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(
        c if c.isalnum() or c in ".-_" else "_"
        for c in file.filename
    )
    rel_path = f"{req.registrar_id}/{req_id}/{timestamp}_{safe_name}"
    abs_path = os.path.join(UPLOAD_BASE, rel_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    with open(abs_path, "wb") as f:
        f.write(content)

    doc = RegistrarDocument(
        registrar_requirement_id=req_id,
        company_id=company_id,
        file_name=file.filename,
        file_path=rel_path,
        file_size=len(content),
        mime_type=file.content_type,
        notes=notes,
        uploaded_by=current_user.id,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    return _envelope({
        "id": doc.id,
        "file_name": doc.file_name,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "status": doc.status,
        "uploaded_at": doc.uploaded_at.isoformat(),
    })


@router.get("/registrar-documents/{doc_id}/download")
async def download_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    doc = await session.get(RegistrarDocument, doc_id)
    if not doc or doc.deleted_at:
        raise HTTPException(404, "Document not found")

    abs_path = os.path.join(UPLOAD_BASE, doc.file_path)
    if not os.path.exists(abs_path):
        raise HTTPException(404, "File not found on server")

    return FileResponse(
        path=abs_path,
        filename=doc.file_name,
        media_type=doc.mime_type,
    )


@router.put("/registrar-documents/{id}/status")
async def update_document_status(
    id: int,
    data: DocumentStatusUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    doc = await session.get(RegistrarDocument, id)
    if not doc or doc.deleted_at:
        raise HTTPException(404, "Document not found")
        
    doc.status = data.status
    if data.notes is not None:
        doc.notes = data.notes
        
    await session.commit()
    return _envelope({"id": doc.id, "status": doc.status})


@router.delete("/registrar-documents/{id}")
async def delete_document(
    id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin)
):
    doc = await session.get(RegistrarDocument, id)
    if not doc or doc.deleted_at:
        raise HTTPException(404, "Document not found")
        
    doc.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return _envelope({"id": id, "message": "Deleted"})


@router.get("/registrar-requirements/{req_id}/history")
async def get_document_history(
    req_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(RegistrarDocument).options(
        selectinload(RegistrarDocument.uploader)
    ).where(
        RegistrarDocument.registrar_requirement_id == req_id
    ).order_by(RegistrarDocument.uploaded_at.desc())
    
    result = await session.execute(stmt)
    docs = result.scalars().all()
    
    response_data = []
    version = len(docs)
    for doc in docs:
        response_data.append({
            "id": doc.id,
            "version": f"v{version}",
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "uploaded_by_name": doc.uploader.name if doc.uploader else "Unknown",
            "is_deleted": doc.deleted_at is not None
        })
        version -= 1
        
    return _envelope(response_data)


@router.post("/registrars/{registrar_id}/companies/{company_id}")
async def link_company_to_registrar(
    registrar_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    # Verify registrar exists
    registrar = await db.get(Registrar, registrar_id)
    if not registrar or registrar.deleted_at:
        raise HTTPException(status_code=404, detail="Registrar not found")

    # Verify company exists
    from app.models import Company
    company = await db.get(Company, company_id)
    if not company or company.deleted_at:
        raise HTTPException(status_code=404, detail="Company not found")

    # Link
    company.registrar_id = registrar.id
    await db.commit()

    return _envelope({"status": "success", "linked": True})


@router.delete("/registrars/{registrar_id}/companies/{company_id}")
async def unlink_company_from_registrar(
    registrar_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    from app.models import Company
    company = await db.get(Company, company_id)
    if not company or company.deleted_at:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.registrar_id != registrar_id:
        raise HTTPException(status_code=400, detail="Company is not linked to this registrar")

    # Unlink
    company.registrar_id = None
    await db.commit()

    return _envelope({"status": "success", "unlinked": True})
