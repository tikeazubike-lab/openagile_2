import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.companies import Company
from app.models.registrars import Registrar

@pytest.mark.asyncio
async def test_link_unlink_company_to_registrar(
    admin_http_client: AsyncClient,
    db_session: AsyncSession,
    test_company: Company
):
    """
    Test the flow of linking a company to a registrar, and then unlinking it.
    This fulfills the UI requirement to add/remove companies from the registrar details card.
    """
    # 1. Create a registrar
    registrar = Registrar(
        name="Test Registrar Ltd",
        email="info@testregistrar.com"
    )
    db_session.add(registrar)
    await db_session.flush()
    registrar_id = registrar.id
    company_id = test_company.id

    # Ensure company has no registrar initially
    assert test_company.registrar_id is None

    # 2. Link company to registrar
    response = await admin_http_client.post(
        f"/api/v1/registrars/{registrar_id}/companies/{company_id}"
    )
    assert response.status_code == 200
    
    # Verify DB state
    await db_session.refresh(test_company)
    assert test_company.registrar_id == registrar_id

    # 3. Unlink company from registrar
    response = await admin_http_client.delete(
        f"/api/v1/registrars/{registrar_id}/companies/{company_id}"
    )
    assert response.status_code == 200

    # Verify DB state
    await db_session.refresh(test_company)
    assert test_company.registrar_id is None
