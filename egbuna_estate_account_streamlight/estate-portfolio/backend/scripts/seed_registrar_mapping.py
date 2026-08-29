#!/usr/bin/env python3
"""
EPM — Repeatable Seed Script: Full NGX Registrar/Company Mapping.

Idempotent — safe to re-run with no duplication. Uses upsert logic.
"""
import asyncio
import logging
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.models import Registrar, Company, CompanyRegistrar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("seed_registrar_mapping")


@dataclass
class RegistrarSpec:
    name: str
    jurisdiction: str = "nigeria"


@dataclass
class CompanySpec:
    name: str
    ticker: str | None = None
    security_type: str = "equity"


@dataclass
class LinkSpec:
    company_ticker: str | None
    company_name: str
    registrar_name: str
    role: str = "primary"


REGISTRARS = [
    RegistrarSpec("Africa Prudential Registrars Limited"),
    RegistrarSpec("Coronation Registrars Limited"),
    RegistrarSpec("First Registrars & Investor Services Limited"),
    RegistrarSpec("Veritas Registrars Limited"),
    RegistrarSpec("DataMax Registrars Limited"),
    RegistrarSpec("CardinalStone Registrars Limited"),
    RegistrarSpec("Greenwich Registrars & Data Solutions Limited"),
    RegistrarSpec("Meristem Registrars & Probate Services Limited"),
    RegistrarSpec("Pace Registrars Limited"),
    RegistrarSpec("Crescent Registrars Limited"),
    RegistrarSpec("United Securities Limited"),
    RegistrarSpec("Carnation Registrars Limited"),
    RegistrarSpec("Computershare UK", jurisdiction="international"),
]

COMPANY_GROUPS = [
    ("Africa Prudential Registrars Limited", [
        ("United Bank for Africa Plc", "UBA", "equity"),
        ("Transnational Corporation Plc", "TRANSCORP", "equity"),
        ("BUA Foods Plc", "BUAFOODS", "equity"),
        ("BUA Cement Plc", "BUACEMENT", "equity"),
        ("Transcorp Hotels Plc", "TRANSPOWER", "equity"),
        ("Africa Prudential Plc", "AFPRUD", "equity"),
        ("United Capital Plc", "UNITEDCAP", "equity"),
        ("Custodian Investment Plc", "CUSTODIAN", "equity"),
        ("Abbey Mortgage Bank Plc", "ABBEYBDS", "equity"),
        ("Haldane McCall Plc", "HALDANE", "equity"),
        ("Austin Laz & Company Plc", "AUSTINLAZ", "equity"),
        ("Infinity Trust Mortgage Bank Plc", "INFINITY", "equity"),
        ("United Capital Balanced Fund", "UCBAL", "mutual_fund"),
        ("United Capital Bond Fund", "UCBOND", "mutual_fund"),
        ("United Capital Equity Fund", "UCEQUITY", "mutual_fund"),
        ("United Capital Eurobond Fund", "UCEURO", "mutual_fund"),
        ("United Capital Money Market Fund", "UCMONEY", "mutual_fund"),
        ("United Capital Wealth for Women Fund", "UCWEALTH", "mutual_fund"),
    ]),
    ("Coronation Registrars Limited", [
        ("Access Holdings Plc", "ACCESS", "equity"),
        ("MTN Nigeria Communications Plc", "MTNN", "equity"),
        ("Dangote Cement Plc", "DANGCEM", "equity"),
        ("Aradel Holdings Plc", "ARADEL", "equity"),
        ("Geregu Power Plc", "GEREGU", "equity"),
        ("Coronation Insurance Plc", "WAPIC", "equity"),
        ("Coronation Infrastructure Fund", "CORINFRA", "mutual_fund"),
        ("AVA Infrastructure Fund", "AVAINFRA", "mutual_fund"),
    ]),
    ("First Registrars & Investor Services Limited", [
        ("First Holdco Plc", "FBNH", "equity"),
        ("Nigerian Breweries Plc", "NB", "equity"),
        ("Stanbic IBTC Holdings Plc", "STANBIC", "equity"),
        ("Oando Plc", "OANDO", "equity"),
        ("Presco Plc", "PRESCO", "equity"),
        ("Okomu Oil Palm Plc", "OKOMOILP", "equity"),
        ("Livestock Feeds Plc", "LIVESTOK", "equity"),
        ("PZ Cussons Nigeria Plc", "PZ", "equity"),
        ("UACN Plc", "UACN", "equity"),
        ("SCOA Nigeria Plc", "SCOA", "equity"),
        ("NCR (Nigeria) Plc", "NCR", "equity"),
        ("FBN Fixed Income Fund", "FBNFIX", "mutual_fund"),
        ("FBN Heritage Fund", "FBNHERIT", "mutual_fund"),
        ("FBN Money Market Fund", "FBNMONEY", "mutual_fund"),
    ]),
    ("Veritas Registrars Limited", [
        ("Zenith Bank Plc", "ZENITHBANK", "equity"),
        ("Dangote Sugar Refinery Plc", "DANGSUGAR", "equity"),
        ("Eterna Plc", "ETERNA", "equity"),
    ]),
    ("DataMax Registrars Limited", [
        ("Guaranty Trust Holding Company Plc", "GTB", "equity"),
        ("Seplat Energy Plc", "SEPLAT", "equity"),
        ("Sterling Financial Holdings Company Plc", "STERLNBANK", "equity"),
        ("Zichis Agro Allied Industries Plc", "ZICHIS", "equity"),
    ]),
    ("CardinalStone Registrars Limited", [
        ("FCMB Group Plc", "FCMB", "equity"),
        ("HBM Nigeria Plc", "HBM", "equity"),
        ("Lafarge Africa Plc", "LAFARGE", "equity"),
        ("Vitafoam Nigeria Plc", "VITAFOAM", "equity"),
        ("Neimeth International Pharmaceuticals Plc", "NEIMETH", "equity"),
    ]),
    ("Greenwich Registrars & Data Solutions Limited", [
        ("Julius Berger Nigeria Plc", "JBERGER", "equity"),
        ("Nestle Nigeria Plc", "NESTLE", "equity"),
        ("Cadbury Nigeria Plc", "CADBURY", "equity"),
        ("Unilever Nigeria Plc", "UNILEVER", "equity"),
        ("CAP Plc", "CAP", "equity"),
        ("Meyer Plc", "MEYER", "equity"),
        ("Greenwich Alpha ETF", "GRNAlpha", "etf"),
    ]),
    ("Meristem Registrars & Probate Services Limited", [
        ("Berger Paints Plc", "BERGER", "equity"),
        ("Conoil Plc", "CONOIL", "equity"),
        ("TotalEnergies Marketing Nigeria Plc", "TOTAL", "equity"),
        ("FTN Cocoa Processors Plc", "FTNCOCOA", "equity"),
        ("CWG Plc", "CWG", "equity"),
        ("Meristem Growth ETF", "MERGROW", "etf"),
        ("Meristem Value ETF", "MERVAL", "etf"),
    ]),
    ("Pace Registrars Limited", [
        ("Honeywell Flour Mill Plc", "HONEYWELL", "equity"),
        ("Fidelity Bank Plc", "FIDELITYBK", "equity"),
        ("Ikeja Hotel Plc", "IKEJAHOTEL", "equity"),
    ]),
    ("Crescent Registrars Limited", [
        ("Wema Bank Plc", "WEMA", "equity"),
        ("AXA Mansard Insurance Plc", "MANSARD", "equity"),
        ("Cutix Plc", "CUTIX", "equity"),
    ]),
    ("United Securities Limited", [
        ("Ecobank Transnational Incorporated", "ETI", "equity"),
        ("AIICO Insurance Plc", "AIICO", "equity"),
        ("Mutual Benefits Assurance Plc", "MUTUALBEN", "equity"),
        ("Sunu Assurances Nigeria Plc", "SUNUASSUR", "equity"),
        ("Nigerian Aviation Handling Company Plc", "NAHCO", "equity"),
    ]),
    ("Carnation Registrars Limited", [
        ("Chams Holding Company Plc", "CHAMS", "equity"),
        ("eTranzact International Plc", "ETRANZACT", "equity"),
        ("Japaul Gold & Ventures Plc", "JAPUAL", "equity"),
        ("Royal Exchange Plc", "ROYALEX", "equity"),
        ("Sovereign Trust Insurance Plc", "SOVEREIGN", "equity"),
        ("Veritas Kapital Assurance Plc", "VERITASKAP", "equity"),
        ("Universal Insurance Plc", "UNIVERSAL", "equity"),
        ("NEM Insurance Plc", "NEM", "equity"),
        ("Consolidated Hallmark Holdings Plc", "CHIPLC", "equity"),
        ("Cornerstone Insurance Plc", "CORNERST", "equity"),
        ("LASACO Assurance Plc", "LASACO", "equity"),
        ("Linkage Assurance Plc", "LINKASSURE", "equity"),
        ("Regency Assurance Plc", "REGALINS", "equity"),
        ("Prestige Assurance Plc", "PRESTIGE", "equity"),
        ("Guinea Insurance Plc", "GUINEAINS", "equity"),
        ("International Energy Insurance Plc", "INTENEGINS", "equity"),
    ]),
]

UNMAPPED_COMPANIES = [
    CompanySpec("Ellah Lakes Plc", "ELLAHLAKES"),
    CompanySpec("Champion Breweries Plc", "CHAMPION"),
    CompanySpec("Golden Guinea Breweries Plc", "GOLDENGUIN"),
    CompanySpec("International Breweries Plc", "INTBREW"),
    CompanySpec("Northern Nigeria Flour Mills Plc", "NNFM"),
    CompanySpec("NASCON Allied Industries Plc", "NASCON"),
    CompanySpec("Union Dicon Salt Plc", "UNIONDICON"),
    CompanySpec("Multi-Trex Integrated Foods Plc", "MULTITREX"),
    CompanySpec("Nigerian Enamelware Plc", "NIGENAMEL"),
    CompanySpec("Ekocorp Plc", "EKOCORP"),
    CompanySpec("Morison Industries Plc", "MORISON"),
    CompanySpec("Fidson Healthcare Plc", "FIDSON"),
    CompanySpec("May & Baker Nigeria Plc", "MBANQ"),
    CompanySpec("Pharma-Deko Plc", "PHARMADEKO"),
    CompanySpec("Omatek Ventures Plc", "OMATEK"),
    CompanySpec("Airtel Africa Plc", "AIRTELAFRI"),
    CompanySpec("Legend Internet Plc", "LEGEND"),
    CompanySpec("Premier Paints Plc", "PREMPAINT"),
    CompanySpec("Beta Glass Plc", "BETAGLAS"),
    CompanySpec("Tripple Gee and Company Plc", "TRIPPLEG"),
    CompanySpec("Industrial & Medical Gases Nigeria Plc", "IMG"),
    CompanySpec("Aluminium Extrusion Ind. Plc", "ALUMEX"),
    CompanySpec("Multiverse Mining and Exploration Plc", "MULTIVERSE"),
    CompanySpec("Thomas Wyatt Nigeria Plc", "THOMASWYAT"),
    CompanySpec("Afromedia Plc", "AFROMEDIA"),
    CompanySpec("R T Briscoe Plc", "RTBRISCOE"),
    CompanySpec("Red Star Express Plc", "REDSTAREX"),
    CompanySpec("Trans-Nationwide Express Plc", "TRANSEX"),
    CompanySpec("Tantalizers Plc", "TANTALIZER"),
    CompanySpec("DAAR Communications Plc", "DAARCOMM"),
    CompanySpec("Academy Press Plc", "ACADEMY"),
    CompanySpec("Learn Africa Plc", "LEARNAFR"),
    CompanySpec("University Press Plc", "UNITYPRESS"),
    CompanySpec("Associated Bus Company Plc", "ABCTRANS"),
    CompanySpec("Eunisell Interlinked Plc", "EUNISELL"),
    CompanySpec("Secure Electronic Technology Plc", "SECUREID"),
    CompanySpec("Skyway Aviation Handling Company Plc", "SKYAVN"),
    CompanySpec("C & I Leasing Plc", "CILEASING"),
    CompanySpec("Caverton Offshore Support Group Plc", "CAVERTON"),
    CompanySpec("Transcorp Power Plc", "TRANSCORPPOWER"),
    CompanySpec("VFD Group Plc", "VFDGROUP"),
    CompanySpec("Chellarams Plc", "CHELLARAM"),
    CompanySpec("Ronchess Global Resources Plc", "RONCHESS"),
    CompanySpec("McNichols Plc", "MCNICHOLS"),
    CompanySpec("LivingTrust Mortgage Bank Plc", "LIVINGTRUST"),
    CompanySpec("MeCure Industries Plc", "MECURE"),
    CompanySpec("Briclinks Africa Plc", "BRICLINKS"),
    CompanySpec("Juli Plc", "JULI"),
    CompanySpec("The Initiates Plc", "THEINITIATES"),
    CompanySpec("Jaiz Bank Plc", "JAIZBANK"),
]

SPECIAL_LINKS = [
    LinkSpec("SEPLAT", "Seplat Energy Plc", "DataMax Registrars Limited", "primary"),
    LinkSpec("SEPLAT", "Seplat Energy Plc", "Computershare UK", "co_registrar"),
    LinkSpec("AFPRUD", "Africa Prudential Plc", "Africa Prudential Registrars Limited", "primary"),
]


async def seed_registrars(session) -> dict:
    created = 0
    existing = 0
    for spec in REGISTRARS:
        result = await session.execute(
            select(Registrar).where(Registrar.name == spec.name)
        )
        reg = result.scalar_one_or_none()
        if reg is None:
            reg = Registrar(name=spec.name, jurisdiction=spec.jurisdiction)
            session.add(reg)
            await session.flush()
            created += 1
        else:
            existing += 1
    return {"created": created, "existing": existing}


async def seed_companies(session) -> dict:
    created = 0
    existing = 0
    seen_tickers = set()

    for registrar_name, companies in COMPANY_GROUPS:
        for name, ticker, sec_type in companies:
            if ticker and ticker in seen_tickers:
                continue
            if ticker:
                seen_tickers.add(ticker)

            result = await session.execute(
                select(Company).where(
                    Company.ticker == ticker if ticker else Company.name == name
                )
            )
            co = result.scalar_one_or_none()
            if co is None:
                co = Company(name=name, ticker=ticker, security_type=sec_type)
                session.add(co)
                await session.flush()
                created += 1
            else:
                existing += 1

    for spec in UNMAPPED_COMPANIES:
        if spec.ticker and spec.ticker in seen_tickers:
            continue
        if spec.ticker:
            seen_tickers.add(spec.ticker)

        result = await session.execute(
            select(Company).where(
                Company.ticker == spec.ticker if spec.ticker else Company.name == spec.name
            )
        )
        co = result.scalar_one_or_none()
        if co is None:
            co = Company(name=spec.name, ticker=spec.ticker, security_type=spec.security_type)
            session.add(co)
            await session.flush()
            created += 1
        else:
            existing += 1

    return {"created": created, "existing": existing}


async def seed_links(session) -> dict:
    created = 0
    existing = 0
    skipped = 0

    for registrar_name, companies in COMPANY_GROUPS:
        result = await session.execute(
            select(Registrar).where(Registrar.name == registrar_name)
        )
        reg = result.scalar_one_or_none()
        if not reg:
            skipped += len(companies)
            continue

        for name, ticker, _sec_type in companies:
            if ticker:
                result = await session.execute(
                    select(Company).where(Company.ticker == ticker)
                )
            else:
                result = await session.execute(
                    select(Company).where(Company.name == name)
                )
            co = result.scalar_one_or_none()
            if not co:
                skipped += 1
                continue

            result = await session.execute(
                select(CompanyRegistrar).where(
                    CompanyRegistrar.company_id == co.id,
                    CompanyRegistrar.registrar_id == reg.id,
                )
            )
            existing_link = result.scalar_one_or_none()
            if existing_link:
                existing += 1
            else:
                link = CompanyRegistrar(
                    company_id=co.id,
                    registrar_id=reg.id,
                    role="primary",
                )
                session.add(link)
                created += 1

    return {"created": created, "existing": existing, "skipped": skipped}


async def seed_special_links(session) -> dict:
    created = 0
    updated = 0
    skipped = 0

    await session.flush()

    for spec in SPECIAL_LINKS:
        if spec.company_ticker:
            result = await session.execute(
                select(Company).where(Company.ticker == spec.company_ticker)
            )
        else:
            result = await session.execute(
                select(Company).where(Company.name == spec.company_name)
            )
        co = result.scalar_one_or_none()
        if not co:
            skipped += 1
            continue

        result = await session.execute(
            select(Registrar).where(Registrar.name == spec.registrar_name)
        )
        reg = result.scalar_one_or_none()
        if not reg:
            skipped += 1
            continue

        result = await session.execute(
            select(CompanyRegistrar).where(
                CompanyRegistrar.company_id == co.id,
                CompanyRegistrar.registrar_id == reg.id,
            )
        )
        existing_link = result.scalar_one_or_none()
        if existing_link:
            if existing_link.role != spec.role:
                existing_link.role = spec.role
                updated += 1
        else:
            link = CompanyRegistrar(
                company_id=co.id,
                registrar_id=reg.id,
                role=spec.role,
            )
            session.add(link)
            created += 1

    return {"created": created, "updated": updated, "skipped": skipped}


async def main(dry_run: bool = False, preview: bool = False) -> int:
    logger.info("Seed registrar mapping — started%s%s", " (preview)" if preview else "", " (dry run)" if dry_run else "")

    if preview:
        async with AsyncSessionLocal() as session:
            reg_result = await seed_registrars(session)
            co_result = await seed_companies(session)
            link_result = await seed_links(session)
            special_result = await seed_special_links(session)

            logger.info("=== PREVIEW (read-only, no changes) ===")
            logger.info("Registrars: %d would be created, %d already exist", reg_result["created"], reg_result["existing"])
            logger.info("Companies: %d would be created, %d already exist", co_result["created"], co_result["existing"])
            logger.info("Links: %d would be created, %d already existing, %d skipped", link_result["created"], link_result["existing"], link_result["skipped"])
            logger.info("Special links: %d would be created, %d already existing, %d skipped", special_result["created"], special_result["existing"], special_result["skipped"])
            logger.info("Unmapped companies (no registrar): %d", len(UNMAPPED_COMPANIES))
        return 0

    async with AsyncSessionLocal() as session:
        async with session.begin():
            reg_result = await seed_registrars(session)
            co_result = await seed_companies(session)
            link_result = await seed_links(session)
            special_result = await seed_special_links(session)

            if dry_run:
                await session.rollback()
                logger.info("Dry run — no changes committed")
            else:
                await session.commit()
                logger.info("Seed complete — changes committed")

    total_companies = co_result["created"] + co_result["existing"]
    total_links = link_result["created"] + link_result["existing"]
    logger.info("=== Summary ===")
    logger.info("Total registrars: %d", reg_result["created"] + reg_result["existing"])
    logger.info("Total companies: %d (%d created, %d pre-existing)", total_companies, co_result["created"], co_result["existing"])
    logger.info("Total company_registrars links: %d", total_links)
    logger.info("Unmapped companies (no registrar): %d", len(UNMAPPED_COMPANIES))
    logger.info("Skipped (missing entity): %d", link_result["skipped"])

    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    preview = "--preview" in sys.argv
    exit_code = asyncio.run(main(dry_run=dry_run, preview=preview))
    sys.exit(exit_code)
