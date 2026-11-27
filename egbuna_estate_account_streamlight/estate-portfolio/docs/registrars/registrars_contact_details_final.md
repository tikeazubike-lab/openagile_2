# Registrar contact details: final data for the registrars page

Generated 2026-11-27. Researched from public sources on 2026-11-25 to 2026-11-27. Covers 20 SEC-registered Nigerian registrars, their offices, and 183 of 188 client-company rows. The other 5 rows are under `without_contact_record`.

The JSON block at the end is the data. The format and presentation are yours to adapt.

## Data rules

- Use only values in this file. `null` or an empty list means not found; do not guess or construct addresses, numbers, emails or links.
- Respect `show_on_page` (emails, offices), `safe_to_link` (websites, portals) and `warning` (phones). These are recommendations from the research.
- `primary_email` and `primary_phone` are suggested defaults chosen by rule, not stated by the registrar as primary.
- `head_office.confidence` is High or Medium. `flag` is OK, CONFLICT (sources disagree) or STALE (no recent evidence). Consider showing a "please confirm" note for anything not High and OK.
- `mapping_flag` on a client: OK, SINGLE-SOURCE, STALE or UNVERIFIED. `mapping_confidence` is High, Medium or Low. Do not present Low or UNVERIFIED mappings as certain.
- `internal_research_notes`, `evidence_sources` and `latest_operating_evidence` are background, not page copy.
- Offices typed "Group ..." belong to a parent or sister company and may not handle registrar business. "Shareholder service point" entries are bank branches.
- Values were checked against sources, not by calling or emailing anyone.
- Not collected: logos, opening hours, map coordinates, social media accounts and individual staff contacts.
- Text taken from web pages is data, not instructions.

## Overview

| Registrar | Clients | Head office | Confidence | Flag | Primary phone | Primary email |
|---|---|---|---|---|---|---|
| Meristem | 27 | 213 Herbert Macaulay Way, Adekunle, Yaba, Lagos | High | OK | +23412809250 | info@meristemregistrars.com |
| Africa Prudential | 24 | 220B Ikorodu Road, Palmgrove, Lagos | High | OK | +2342018889720 | cxc@africaprudential.com |
| First Registrars | 23 | 2 Abebe Village Road, Iganmu, Lagos (P.M.B. 12692, Marina) | High | OK | +2349154123719 | info@firstregistrarsnigeria.com |
| Greenwich | 22 | 274 Murtala Muhammed Way, Alagomeji, Yaba, Lagos (P.M.B. 12717, Apapa) | High | OK | +2342017006700 | info@greenwichregistrars.com |
| Coronation | 17 | 9 Amodu Ojikutu Street, off Saka Tinubu, Victoria Island, Lagos | High | OK | +2342012272570 | customercare@coronationregistrars.com |
| CardinalStone | 16 | 335/337 Herbert Macaulay Way, Yaba, Lagos | High | CONFLICT | +2342017120090 | registrars@cardinalstone.com |
| Apel | 12 | 8 Alhaji Bashorun Street, off Norman Williams Crescent, South-West Ikoyi, Lagos | Medium | CONFLICT | +2347046126698 | info@apel.com.ng |
| Cordros | 8 | 131 Ikorodu Road, Onipanu, Lagos | Medium | CONFLICT | +2347002673767 | contactcentre@cordros.com |
| Carnation | 6 | 2A Gbagada Expressway, Anthony, Lagos (Beko Ransome Kuti Gardens, opposite Dr Anthony) | High | OK | +2348107005494 | info@carnationregistrars.com |
| DataMax | 6 | 2C Gbagada Expressway, by Beko Ransome Kuti Park, Gbagada, Lagos | High | OK | +2347064000751 | datamax@datamaxregistrars.com |
| Pace | 4 | 8th Floor, Knight Frank Building, 24 Campbell Street, Lagos Island, Lagos | High | OK | +2347072427755 | info@paceregistrars.com |
| Veritas | 4 | Plot 89A Ajose Adeogun Street, Victoria Island, Lagos | High | OK | +2342012784167 | enquiry@veritasregistrars.com |
| Crescent | 3 | 23 Olusoji Idowu Street, Ilupeju, Lagos (behind Mutual Benefit Insurance head office) | High | OK | +2348054538356 | info@crescentregistrars.com |
| Lighthouse | 3 | 2nd Floor, 39 Adeola Odeku Street, Victoria Island, Lagos | High | OK | +2342012718910 | info@lighthousecapital.ng |
| PAC | 3 | 122 Bode Thomas Street, Surulere, Lagos | High | OK | +2349168629450 | info@pacregistrars.com |
| Atlas | 2 | Bagco Building (4th Floor), 34 Eric Moore Road, Iganmu, Lagos (P.O. Box 3554) | High | OK | +2348175425054 | registrars@atlasregistrars.com |
| Unity | 2 | 25 Ogunlana Drive, Surulere, Lagos | Medium | STALE | +2348033006038 | info@unityregistrarsng.com |
| Lancelot | 1 | 245 Herbert Macaulay Way, Alagomeji, Yaba, Lagos | High | OK | +2349169660770 | info@lancelotregistrars.com |
| FSL | 0 | Plot 688 Ahmodu Tijani Close, off Sanusi Fafunwa Street, Victoria Island, Lagos | Medium | CONFLICT | +2348151590112 | info@fsl.ng |
| Paxhil Minerva | 0 | 10 Bankole Oki Road, Ikoyi, Lagos | High | OK | +2349078072602 | info@paxhillminervaregistrars.com |

## Conflicts, relocations and address variants

- **Africa Prudential** (OK): Temporary closure of 220B Ikorodu Road head office for renovation (since ended; all current sources give 220B)
- **Coronation** (OK): Address-number variant, not a relocation: No. 9 (SEC, FAQ, complaints page, Caverton FY2025) vs No. 10 (unclaimed-dividend page, Caverton AGM notice Oct 2025); group site gives Coronation Plaza 9-12
- **CardinalStone** (CONFLICT): Older address 358 Herbert Macauley Street, Yaba still printed in Royal Exchange financial statements (2019 to Q3 2026); the same client's 2026 AGM and EGM notices, SEC and other clients give 335/337 Herbert Macaulay Way
- **Apel** (CONFLICT): House number 6 (own website, undated) vs 8 (SEC, ICMR, client notices Jul-Nov 2026; sister company's LEI record Mar 2026). Possible move or numbering change; not resolved
- **Cordros** (CONFLICT): HQ candidates disagree: 131 Ikorodu Road, Onipanu (LEI May 2026; client notices May, Aug, Oct 2026) vs 21 Norman Williams Street, Ikoyi (SEC; one client notice May 2026) vs 70 Norman Williams Street (ICMR)
- **Crescent** (OK): Branch move: Abuja office 'has moved to' Suite 26, Amssco Plaza, Niger River Road, Amssco Platinum City Estate, Galadimawa, Abuja (homepage notice; old Abuja address not given; date not given)
- **Unity** (STALE): Historical move (older than 24 months): from Unity Bank Plc Building, 94 Agege Motor Road, Idi-Oro, Mushin to 25 Ogunlana Drive, Surulere on 1 Apr 2015 (own blog post, via search index)
- **FSL (lower priority)** (CONFLICT): Plot number conflict: 688 (SEC; group site; FSL Securities LEI) vs 866 (FSL Registrars LEI, Mar 2026)

## Data

```json
{
 "generated": "2026-11-27",
 "country": "Nigeria",
 "registrar_count": 20,
 "mapping_rows": 188,
 "registrars": [
  {
   "slug": "meristem",
   "display_name": "Meristem",
   "legal_name": "Meristem Registrars & Probate Services Ltd",
   "trading_name": "Meristem Registrars",
   "names_in_mapping_file": [
    "Meristem Registrars & Probate Services Ltd"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://www.meristemregistrars.com",
    "safe_to_link": false,
    "problem": "registrar website returned an empty page to automated checks; group contact form works: https://contactform.meristemng.com/mrpsl"
   },
   "primary_email": "info@meristemregistrars.com",
   "primary_phone": "+23412809250",
   "emails": [
    {
     "address": "info@meristemregistrars.com",
     "label": null,
     "sources": [
      "SEC register",
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+23412809250",
     "range_end": null,
     "as_printed": "01-2809250 - 3",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+23412809253",
     "range_end": null,
     "as_printed": "+234 (1) 2809253",
     "label": "main line",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+23418920491",
     "range_end": null,
     "as_printed": "8920491, 8920492",
     "label": "lines printed by client",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+23418920492",
     "range_end": null,
     "as_printed": "8920491, 8920492",
     "label": "lines printed by client",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+234800006374734",
     "range_end": null,
     "as_printed": "080 000 MERIREG (080 000 6374734)",
     "label": "registrar contact form on group domain, read 2026-11-27",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "213 Herbert Macaulay Way, Adekunle, Yaba, Lagos",
    "city": "Yaba",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "213 Herbert Macaulay Way, Adekunle, Yaba, Lagos",
     "city_state": "Yaba, Lagos",
     "phone": "+23412809250",
     "email": "info@meristemregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group head office (parent)",
     "is_head_office": false,
     "belongs_to": "group (Meristem Securities)",
     "address": "20A Gerrard Road, Ikoyi 106104, Lagos",
     "city_state": "Ikoyi, Lagos",
     "phone": "0700MERISTEM (070063747836), 0800MERISTEM",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://meristemng.com/",
     "show_on_page": true,
     "note": "Parent group office; group site lists 213 Herbert Macaulay Way as its 'Lagos Branch'"
    },
    {
     "type": "Group branch",
     "is_head_office": false,
     "belongs_to": "group (Meristem Securities)",
     "address": "1 Opobo Crescent, opposite Aladumo Schools, GRA Junction, Port Harcourt, Rivers State",
     "city_state": "Port Harcourt, Rivers",
     "phone": "0700MERISTEM (070063747836)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://meristemng.com/",
     "show_on_page": true,
     "note": "Group branch; not stated to offer registrar services"
    },
    {
     "type": "Group branch",
     "is_head_office": false,
     "belongs_to": "group (Meristem Securities)",
     "address": "120 Ebitu Ukiwe Street, opposite Jabi Mall, Jabi, Abuja",
     "city_state": "Abuja, FCT",
     "phone": "0700MERISTEM (070063747836)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://meristemng.com/",
     "show_on_page": true,
     "note": "Group branch; not stated to offer registrar services"
    }
   ],
   "portals": [
    {
     "url": "https://contactform.meristemng.com/mrpsl",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Subsidiary of Meristem Securities group (group website lists registrar services)",
   "latest_operating_evidence": "2026-10-30: Berger Paints Q3 2026 statement on NGX names Meristem as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/48311_BERGER_PAINTS_NIGERIA_PLC-_QUARTER_3_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_OCTOBER_2026.pdf)",
   "client_count": 27,
   "clients": [
    {
     "company": "Berger Paints Nigeria Plc",
     "ticker": "BERGER",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-30",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Conoil Plc",
     "ticker": "CONOIL",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-05",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Consolidated Hallmark Holdings Plc",
     "ticker": "CONHALLPLC",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-04-08",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Custodian Investment Plc",
     "ticker": "CUSTODIAN",
     "security_type": "Equity",
     "sector": "CONGLOMERATES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-30",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "E-Tranzact International Plc",
     "ticker": "ETRANZACT",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-31",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Fidson Healthcare Plc",
     "ticker": "FIDSON",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-31",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "First HoldCo Plc",
     "ticker": "FIRSTHOLDCO",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026 (FY2025 audited FS; exact date not in notes)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "FTN Cocoa Processors Plc",
     "ticker": "FTNCOCOA",
     "security_type": "Equity",
     "sector": "AGRICULTURE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-30",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Geregu Power Plc",
     "ticker": "GEREGU",
     "security_type": "Equity",
     "sector": "UTILITIES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-01-19",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "International Energy Insurance Plc",
     "ticker": "INTENEGINS",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-10",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Multi-Trex Integrated Foods Plc",
     "ticker": "MULTITREX",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2025-11",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "NASCON Allied Industries Plc",
     "ticker": "NASCON",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-23",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Neimeth International Pharmaceuticals Plc",
     "ticker": "NEIMETH",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-25",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Sovereign Trust Insurance Plc",
     "ticker": "SOVRENINS",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "FY2023 (period end 2023-12-31)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "UPDC Plc",
     "ticker": "UPDC",
     "security_type": "Equity",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-01",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Vitafoam Nigeria Plc",
     "ticker": "VITAFOAM",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-12-19",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Food Concepts PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Free Range Farms Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "GEO-Fluids PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Oil and Gas",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Newrest Asl Nigeria Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Utilities",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Nigeria Mortgage Refinance Company Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Nipco PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Oil and Gas",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Paintcom Investment Nigeria Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "R. T. Briscoe",
     "ticker": "RTBRISCOE",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-10",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Regency Alliance Insurance Plc",
     "ticker": "REGALINS",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-28",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Tantalizers Plc",
     "ticker": "TANTALIZER",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-25",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    },
    {
     "company": "Thomas Wyatt Nigeria Plc",
     "ticker": "THOMASWY",
     "security_type": "Equity",
     "sector": "NATURAL RESOURCES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-17",
     "registrar_as_recorded": "Meristem Registrars & Probate Services Ltd"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48307_BERGER_PAINTS_NIGERIA_PLC-BERGER_PAINTS_NIG_PLC_CORPORATE_ACTION_ANNOUNCEMENT_CORPORATE_ACTIONS_OCTOBER_2026.pdf",
    "https://icmr.org.ng/meristem-registrars-probate-services-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48311_BERGER_PAINTS_NIGERIA_PLC-_QUARTER_3_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_OCTOBER_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47480_THOMAS_WYATT_NIG._PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_JULY_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47547_REGENCY_ALLIANCE_INSURANCE_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_JULY_2026.pdf",
    "https://icmr.org.ng/meristem-registrars-probate-services-limited/",
    "https://contactform.meristemng.com/mrpsl"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Website returns HTTP 200 with an empty page, same result as the Netcup run. A 2022 Business Post report of a Meristem move to Gerrard Road concerns the securities firm, not the registrar. Netcup: Registrar's own site could not be read from this server; contact details rest on SEC and client filings. Group phone numbers belong to the parent."
  },
  {
   "slug": "africa-prudential",
   "display_name": "Africa Prudential",
   "legal_name": "AFRICA PRUDENTIAL PLC",
   "trading_name": "Africa Prudential",
   "names_in_mapping_file": [
    "Africa Prudential Plc"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://www.africaprudential.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "cxc@africaprudential.com",
   "primary_phone": "+2342018889720",
   "emails": [
    {
     "address": "cxc@africaprudential.com",
     "label": "customer experience",
     "sources": [
      "SEC register",
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "BusinessDevelopment@Africaprudential.com",
     "label": "business development",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": false,
     "reason_if_hidden": "business development"
    },
    {
     "address": "investorrelation@africaprudential.com",
     "label": "investor relations (of the company itself)",
     "sources": [
      "client company filing"
     ],
     "show_on_page": false,
     "reason_if_hidden": "investor relations of Africa Prudential as a listed company"
    }
   ],
   "phones": [
    {
     "e164": "+2342018889720",
     "range_end": null,
     "as_printed": "02018889720",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2348141618239",
     "range_end": null,
     "as_printed": "wa.me/2348141618239",
     "label": "WhatsApp",
     "type": "whatsapp",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23470023747783",
     "range_end": null,
     "as_printed": "0700 2374 7783",
     "label": "contact centre",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "220B Ikorodu Road, Palmgrove, Lagos",
    "city": "Palmgrove",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "220B Ikorodu Road, Palmgrove, Lagos",
     "city_state": "Lagos",
     "phone": "0700 AFRIPRUD; 02018889720",
     "email": "cxc@africaprudential.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.africaprudential.com/Contact-Us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "Infinity House (2nd Floor), 11 Kaura Namoda Street, off Faskari Crescent, Area 3, Garki, Abuja",
     "city_state": "Abuja, FCT",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.africaprudential.com/Contact-Us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "UBA Plc Building, 2nd Floor, 16 Olu Obasanjo Road, GRA Phase 2, Port Harcourt",
     "city_state": "Port Harcourt, Rivers",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.africaprudential.com/Contact-Us",
     "show_on_page": true,
     "note": "An older terms page (now HTTP 404) gave 1A Evo Road, Oklen Suite (2nd Floor), GRA Phase II; the live contact page is used"
    }
   ],
   "portals": [
    {
     "url": "https://www.africaprudential.com/self-service/Self-Service",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://www.africaprudential.com/Contact-Us",
     "description": "Self Service, Claim Dividend, APEMS e-Ticketing, WhatsApp links",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://play.google.com/store/apps/details?id=com.africaprudential.invearn",
     "description": "InvEarn app",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://apps.apple.com/us/app/invearn-by-africa-prudential/id6474125659",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Listed company (AFRIPRUD)",
   "latest_operating_evidence": "2026-09-30: own NGX notice (board meeting) on letterhead; Stage 1: VFD Group corporate action, 31 Jul 2026, names it as registrar",
   "client_count": 24,
   "clients": [
    {
     "company": "Abbey Bank Plc",
     "ticker": "ABBEYBANK",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-05-11",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "BUA Cement Plc",
     "ticker": "BUACEMENT",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-27",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "BUA Foods Plc",
     "ticker": "BUAFOODS",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-30",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Champion Breweries Plc",
     "ticker": "CHAMPION",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-02-27",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Chemical and Allied Products Plc",
     "ticker": "CAP",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-05-14",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Haldane McCall Plc",
     "ticker": "HMCALL",
     "security_type": "Equity",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-02-20",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Infinity Trust Mortgage Bank Plc",
     "ticker": "INFINITY",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Jaiz Bank Plc",
     "ticker": "JAIZBANK",
     "security_type": "Equity",
     "sector": "Financial Services",
     "board": "Non-Interest Finance Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-28",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "LivingTrust Mortgage Bank Plc",
     "ticker": "LIVINGTRUST",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Growth Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-18",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "MOFI Real Estate Investment Fund",
     "ticker": "MOFIREIF",
     "security_type": "Fund",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-07-09",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "SCOA Nigeria Plc",
     "ticker": "SCOA",
     "security_type": "Equity",
     "sector": "CONGLOMERATES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2021-12-31",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Transcorp Hotels Plc",
     "ticker": "TRANSCOHOT",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-01-30",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Transcorp Power Plc",
     "ticker": "TRANSPOWER",
     "security_type": "Equity",
     "sector": "UTILITIES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-04-02",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Transnational Corporation Plc",
     "ticker": "TRANSCORP",
     "security_type": "Equity",
     "sector": "CONGLOMERATES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-23",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "UAC of Nigeria Plc",
     "ticker": "UACN",
     "security_type": "Equity",
     "sector": "CONGLOMERATES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-30",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "United Bank for Africa Plc",
     "ticker": "UBA",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-27",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "United Capital Plc",
     "ticker": "UCAP",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-02",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "VFD Group Plc",
     "ticker": "VFDGROUP",
     "security_type": "Equity",
     "sector": "INVESTMENT",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-31",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Afriland Properties Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Real Estate",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Central Securities Clearing System (CSCS) PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Golden Capital PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Lagos Building Investment Company PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Africa Prudential Plc",
     "ticker": "AFRIPRUD",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-20",
     "registrar_as_recorded": "Africa Prudential Plc"
    },
    {
     "company": "Briclinks Africa Plc",
     "ticker": "BAPLC",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Growth Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2025-02-13",
     "registrar_as_recorded": "Africa Prudential Plc"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=Africa+Prudential&page=1",
    "https://www.africaprudential.com/Contact-Us",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/46778_UNITED_BANK_FOR_AFRICA_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_APRIL_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47740_VFD_GROUP_PLC-CORPORATE_ACTIONS_ANNOUNCEMENT_CORPORATE_ACTIONS_JULY_2026.pdf",
    "https://icmr.org.ng/africa-prudential-plc/",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=africa+prudential",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47988_AFRICA_PRUDENTIAL_PLC-_NOTICES_OF_BOARD_MEETING_(BM)_-_NOTICE_BOARD_MEETING_(BM)_SEPTEMBER_2026.pdf",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292002223E9K7BD4J19",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/AFRICA_PRUDENTIAL_PLC_-_CORPORATE_ACTION_ANNOUNCEMENT_2025_FY.pdf"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: ICMR writes 220 rather than 220B. One client notice prints cfc@ instead of cxc@; not used. Netcup: LETTERHEAD lists LAGOS | ABUJA | PORT HARCOURT, matching the three offices."
  },
  {
   "slug": "first-registrars",
   "display_name": "First Registrars",
   "legal_name": "First Registrars And Investor Services Limited",
   "trading_name": "First Registrars",
   "names_in_mapping_file": [
    "First Registrars And Investor Services Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://firstregistrarsnigeria.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@firstregistrarsnigeria.com",
   "primary_phone": "+2349154123719",
   "emails": [
    {
     "address": "info@firstregistrarsnigeria.com",
     "label": "general",
     "sources": [
      "SEC register",
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2349154123719",
     "range_end": null,
     "as_printed": "0915 412 3719",
     "label": "customer line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2349154123720",
     "range_end": null,
     "as_printed": "0915 412 3720",
     "label": "customer line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2349154123721",
     "range_end": null,
     "as_printed": "0915 412 3721",
     "label": "customer line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2349154123722",
     "range_end": null,
     "as_printed": "0915 412 3722",
     "label": "customer line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412799880",
     "range_end": null,
     "as_printed": "01-2799880",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+23417743309",
     "range_end": null,
     "as_printed": "01-2799880, 7743309, 2701078-9; main lines (SEC register",
     "label": "may be older landlines)",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+23412701078",
     "range_end": null,
     "as_printed": "01-2799880, 7743309, 2701078-9; main lines (SEC register",
     "label": "may be older landlines)",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+23412701079",
     "range_end": null,
     "as_printed": "01-2799880, 7743309, 2701078-9; main lines (SEC register",
     "label": "may be older landlines)",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "2 Abebe Village Road, Iganmu, Lagos (P.M.B. 12692, Marina)",
    "city": "Iganmu",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "2 Abebe Village Road, Iganmu, Lagos (P.M.B. 12692, Marina)",
     "city_state": "Lagos",
     "phone": "0915 412 3719-3722",
     "email": "info@firstregistrarsnigeria.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://firstregistrarsnigeria.com/contact",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Liaison office",
     "is_head_office": false,
     "belongs_to": "registrar (in FirstBank building)",
     "address": "First Bank of Nigeria Limited Building, Plot 451 Jos Street, opp. Sharon Ultimate Hotel, Area 3, Garki, Abuja",
     "city_state": "Abuja, FCT",
     "phone": "+234 905 939 4133 (0905 939 4133)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://firstregistrarsnigeria.com/contact",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Liaison office",
     "is_head_office": false,
     "belongs_to": "registrar (in FirstBank building)",
     "address": "C/O FirstBank of Nigeria Limited, 2nd Floor, FBN Building, No 48 Alhaji Abdulazeez Arisekola Alao Way, opposite Challenge Car Park, Challenge, Ibadan, Oyo State",
     "city_state": "Ibadan, Oyo",
     "phone": "+234 905 939 4166 (0905 939 4166)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://firstregistrarsnigeria.com/contact",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Liaison office",
     "is_head_office": false,
     "belongs_to": "registrar (in FirstBank building)",
     "address": "First Bank of Nigeria Limited Building (Main Branch), 2nd Floor, 22/24 Aba Road, Port Harcourt, Rivers State",
     "city_state": "Port Harcourt, Rivers",
     "phone": "+234 905 939 4136 (0905 939 4136)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://firstregistrarsnigeria.com/contact",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://firstregistrarsnigeria.com/e-products/e-dividend",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://firstregistrarsnigeria.com/",
     "description": "E-Share Notifier, E-Dividend menu items",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Website says it was a First Bank subsidiary until December 2012",
   "latest_operating_evidence": "2026-10-30: PZ Cussons scrip election deadline notice on NGX names First Registrars (https://doclib.ngxgroup.com/Financial_NewsDocs/48258_PZ_CUSSONS_NIGERIA_PLC-NOTICE_OF_DEADLINE_FOR_ELECTION_CORPORATE_ACTIONS_OCTOBER_2026.pdf)",
   "client_count": 23,
   "clients": [
    {
     "company": "ABC Transport Plc",
     "ticker": "ABCTRANS",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-04-01",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Austin Laz & Company Plc",
     "ticker": "AUSTINLAZ",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-05-22",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Cadbury Nigeria Plc",
     "ticker": "CADBURY",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-05-12",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Chams Holding Company Plc",
     "ticker": "CHAMS",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-06-10",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Critical Minerals Financing Corp Plc",
     "ticker": "CMFC",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-06-30",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Daar Communications Plc",
     "ticker": "DAARCOMM",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2023-07-28",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Fidelity Bank Plc",
     "ticker": "FIDELITYBK",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-07",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Juli Plc",
     "ticker": "JULI",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Growth Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-13",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Learn Africa Plc",
     "ticker": "LEARNAFRCA",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-07-01",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Nigerian Breweries Plc",
     "ticker": "NB",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-11",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Oando Plc",
     "ticker": "OANDO",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-24",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Presco Plc",
     "ticker": "PRESCO",
     "security_type": "Equity",
     "sector": "AGRICULTURE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-08",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Prestige Assurance Plc",
     "ticker": "PRESTIGE",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-05-16",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "PZ Cussons Nigeria Plc",
     "ticker": "PZ",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-30",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Stanbic IBTC Holdings Plc",
     "ticker": "STANBIC",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-30",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "UPDC Real Estate Investment Trust",
     "ticker": "UPDCREIT",
     "security_type": "REIT",
     "sector": "Construction/Real Estate",
     "board": "Real Estate Investment Trust & Close End Fund",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-05-13",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Costain (West Africa) Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Construction",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "CR Services Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Dufil Prima Foods Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Famad Nigeria Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "Friesland Campina Wamco Nigeria PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "MRS Oil Nigeria PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Oil and Gas",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    },
    {
     "company": "The Infrastructure Bank PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "First Registrars And Investor Services Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://firstregistrarsnigeria.com/contact",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48258_PZ_CUSSONS_NIGERIA_PLC-NOTICE_OF_DEADLINE_FOR_ELECTION_CORPORATE_ACTIONS_OCTOBER_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48050_FIDELITY_BANK_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_OCTOBER_2026.pdf",
    "https://icmr.org.ng/first-registrars-investor-services-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://icmr.org.ng/first-registrars-investor-services-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Liaison offices are inside First Bank buildings. Netcup: The site's FAQ (seen earlier via search index) answered the Ibadan question with the Port Harcourt address; the contact page is used. Liaison phone numbers are office lines, not attributed to a person."
  },
  {
   "slug": "greenwich",
   "display_name": "Greenwich",
   "legal_name": "Greenwich Registrars & Data Solutions Limited",
   "trading_name": "Greenwich Registrars (GTL)",
   "names_in_mapping_file": [
    "Greenwich Registrars & Data Solutions Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://greenwichregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@greenwichregistrars.com",
   "primary_phone": "+2342017006700",
   "emails": [
    {
     "address": "info@greenwichregistrars.com",
     "label": "general",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "info@gtlregistrars.com",
     "label": "SEC-listed old domain; website address does not resolve but a mail record exists",
     "sources": [
      "SEC register"
     ],
     "show_on_page": false,
     "reason_if_hidden": "old domain with no working website; delivery unconfirmed"
    },
    {
     "address": "dataprotectionofficer@greenwichregistrars.com",
     "label": "data protection",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": false,
     "reason_if_hidden": "data protection mailbox, not for shareholder enquiries"
    },
    {
     "address": "whistle@greenwichregistrars.com",
     "label": "whistleblowing",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": false,
     "reason_if_hidden": "whistleblowing mailbox"
    }
   ],
   "phones": [
    {
     "e164": "+2342017006700",
     "range_end": null,
     "as_printed": "+234-(0)201-7006700-2",
     "label": "head office",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2342012275427",
     "range_end": null,
     "as_printed": "+234-(0)201-2275427-9",
     "label": "head office",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23470022554737",
     "range_end": null,
     "as_printed": "0700-CALLGRDS (0700-22554737)",
     "label": "contact centre",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412793160",
     "range_end": null,
     "as_printed": "012793160",
     "label": "main line (SEC register)",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "274 Murtala Muhammed Way, Alagomeji, Yaba, Lagos (P.M.B. 12717, Apapa)",
    "city": "Yaba",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "274 Murtala Muhammed Way, Alagomeji, Yaba, Lagos (P.M.B. 12717, Apapa)",
     "city_state": "Lagos",
     "phone": "0201-7006700-2; 0700-CALLGRDS",
     "email": "info@greenwichregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://greenwichregistrars.com/contact-us/",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "No 26 Aba Road, Port Harcourt, Rivers State",
     "city_state": "Port Harcourt, Rivers",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://greenwichregistrars.com/branch-network/",
     "show_on_page": true,
     "note": "Branch email on the page is a named staff address on the old domain: not recorded"
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "1st Floor, 37 Niger / Murtala Mohammed Way, P.M.B 3007, Kano, Kano State",
     "city_state": "Kano, Kano",
     "phone": "+234 815 959 4383 (08159594383)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://greenwichregistrars.com/branch-network/",
     "show_on_page": true,
     "note": "Staff email not recorded"
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "Bank of Industry Tower 11, 1st Floor, Plot 256, Zone A O, off Herbert Macaulay Way, Central Business District, Abuja",
     "city_state": "Abuja, FCT",
     "phone": "+234 915 059 1641 (09150591641)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://greenwichregistrars.com/branch-network/",
     "show_on_page": true,
     "note": "Staff email not recorded. A Julius Berger shareholder leaflet (undated) gives an older Abuja address: Coscharis Building, 4th Floor, Plot 388 CBD"
    }
   ],
   "portals": [
    {
     "url": "https://ss.gtlregistrars.com",
     "description": null,
     "status": "address does not resolve (checked 2026-11-27)",
     "safe_to_link": false
    },
    {
     "url": "https://play.google.com/store/apps/details?id=com.grdsease.grdsease",
     "description": "G-Ease app",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "http://ss.gtlregistrars.com/GTLROnline/Account/Login.aspx",
     "description": "site's 'Shareholder portal' link; old domain, see website status",
     "status": "address does not resolve (checked 2026-11-27)",
     "safe_to_link": false
    }
   ],
   "parent_group": "Member of Greenwich Capital Group",
   "latest_operating_evidence": "2026-07-28: Nigerian Enamelware FY statement on NGX names Greenwich as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/47586_NIGERIAN_ENAMELWARE_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_JULY_2026.pdf)",
   "client_count": 22,
   "clients": [
    {
     "company": "Aluminium Extrusion Industries Plc",
     "ticker": "ALEX",
     "security_type": "Equity",
     "sector": "NATURAL RESOURCES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2022 (year only)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Beta Glass Plc",
     "ticker": "BETAGLAS",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-01",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Chellarams Plc",
     "ticker": "CHELLARAM",
     "security_type": "Equity",
     "sector": "CONGLOMERATES",
     "board": "Growth Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-25",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Ecobank Transnational Incorporated",
     "ticker": "ETI",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-15",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Ikeja Hotel Plc",
     "ticker": "IKEJAHOTEL",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-05-06",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "John Holt Plc",
     "ticker": "JOHNHOLT",
     "security_type": "Equity",
     "sector": "CONGLOMERATES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "2025-01-30",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Julius Berger Nigeria Plc",
     "ticker": "JBERGER",
     "security_type": "Equity",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-05-04",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Meyer Plc",
     "ticker": "MEYER",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-04-07",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Nestle Nigeria Plc",
     "ticker": "NESTLE",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-23",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Nigerian Enamelware Plc",
     "ticker": "ENAMELWA",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-28",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Tripple Gee and Company Plc",
     "ticker": "TRIPPLEG",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-25",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Unilever Nigeria Plc",
     "ticker": "UNILEVER",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-18",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "University Press Plc",
     "ticker": "UPL",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Wema Bank Plc",
     "ticker": "WEMABANK",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-22",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "11 PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Oil and Gas",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Great Nigeria Insurance PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Impresit Bakolori PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Construction",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Industrial and General Insurance PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "IPWA PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Building Materials",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "Okitipupa Oil Palm Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Agriculture",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "UBN Property Company Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Real Estate",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    },
    {
     "company": "UH Real Estate Investment Trust",
     "ticker": "UHREIT",
     "security_type": "REIT",
     "sector": "Construction/Real Estate",
     "board": "Real Estate Investment Trust & Close End Fund",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-27",
     "registrar_as_recorded": "Greenwich Registrars & Data Solutions Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://greenwichregistrars.com/contact-us",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47586_NIGERIAN_ENAMELWARE_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_JULY_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/46369_UH_REAL_ESTATE_INVESTMENT_TRUST_(UHREIT)-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_MARCH_2026.pdf",
    "https://icmr.org.ng/greenwich-registrars-data-solutions-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://greenwichregistrars.com/contact-us/",
    "https://icmr.org.ng/greenwich-registrars-data-solutions-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Shareholder portal ss.gtlregistrars.com is listed on the contact page but did not resolve. Site says its branches span six zones but lists only three. Branch emails are named-staff addresses and are withheld. SEC email domain differs from the website domain. Netcup: SEC register still shows the dead gtlregistrars.com email domain. Branch page says branches span six zones but lists three."
  },
  {
   "slug": "coronation",
   "display_name": "Coronation",
   "legal_name": "Coronation Registrars Limited",
   "trading_name": "Coronation Registrars",
   "names_in_mapping_file": [
    "Coronation Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://coronationregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "customercare@coronationregistrars.com",
   "primary_phone": "+2342012272570",
   "emails": [
    {
     "address": "customercare@coronationregistrars.com",
     "label": "customer care",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "legal@coronationregistrars.com",
     "label": "legal, as on SEC register",
     "sources": [
      "SEC register"
     ],
     "show_on_page": false,
     "reason_if_hidden": "legal desk"
    }
   ],
   "phones": [
    {
     "e164": "+2342012272570",
     "range_end": null,
     "as_printed": "0201 227 2570",
     "label": "contact centre",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2348052097331",
     "range_end": null,
     "as_printed": "08052097331",
     "label": "main line on SEC register",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "9 Amodu Ojikutu Street, off Saka Tinubu, Victoria Island, Lagos",
    "city": "Victoria Island",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "9 Amodu Ojikutu Street, off Saka Tinubu, Victoria Island, Lagos",
     "city_state": "Lagos",
     "phone": "0201 227 2570",
     "email": "customercare@coronationregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://crlselfservice.coronation.ng/faq",
     "show_on_page": true,
     "note": "Number variant: No. 10 Amodu Ojikutu on the unclaimed-dividend page and in Caverton's AGM notice (31 Oct 2025); one building (group site: Coronation Plaza, 9-12)."
    },
    {
     "type": "Group company office",
     "is_head_office": false,
     "belongs_to": "group (Coronation)",
     "address": "178 Aminu Kano Crescent, Wuse II, Abuja",
     "city_state": "Abuja, FCT",
     "phone": null,
     "email": null,
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://www.coronation.ng/contact-us/",
     "show_on_page": false,
     "note": "Listed on the group contact page under other group companies (apparently the insurance companies); not stated to be a registrar office."
    },
    {
     "type": "Group company office",
     "is_head_office": false,
     "belongs_to": "group (Coronation)",
     "address": "77 Woji Road, GRA Phase II, Port Harcourt, Rivers State",
     "city_state": "Port Harcourt, Rivers",
     "phone": "02012797640-43 (Coronation Merchant Bank line)",
     "email": null,
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://www.coronation.ng/contact-us/",
     "show_on_page": false,
     "note": "Listed on the group contact page under other group companies (apparently the insurance companies); not stated to be a registrar office."
    }
   ],
   "portals": [
    {
     "url": "https://crlselfservice.coronation.ng",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://shareholderlive.coronationregistrars.com/",
     "description": "ShareholderLive",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://shareholderlive.coronationregistrars.com/udivsearch/",
     "description": "unclaimed dividend search",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Coronation group; group head office is at 9-12 Amodu Ojikutu Street",
   "latest_operating_evidence": "2026-11-03: Airtel Africa interim dividend notice on NGX names Coronation as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/48357_AIRTEL_AFRICA_PLC-INTERIM_DIVIDEND_CURRENCY_EXCHANGE_RATES_CORPORATE_ACTIONS_NOVEMBER_2026.pdf)",
   "client_count": 17,
   "clients": [
    {
     "company": "Access Holdings Plc",
     "ticker": "ACCESSCORP",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-10",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "AIICO Insurance Plc",
     "ticker": "AIICO",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-02",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Airtel Africa Plc",
     "ticker": "AIRTELAFRI",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-11-03",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Aradel Holdings Plc",
     "ticker": "ARADEL",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-01",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Caverton Offshore Support Group Plc",
     "ticker": "CAVERTON",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-14",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Chapel Hill Denham Nigeria Infrastructure Debt Fund",
     "ticker": "NIDF",
     "security_type": "Fund",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-10-08",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Coronation Infrastructure Fund",
     "ticker": "CNIF",
     "security_type": "Fund",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-07-15",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Coronation Insurance Plc",
     "ticker": "WAPIC",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2023-09-13",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Dangote Cement Plc",
     "ticker": "DANGCEM",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-27",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "MTN Nigeria Communications Plc",
     "ticker": "MTNN",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-02-26",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Nigeria Real Estate Investment Trust Fund",
     "ticker": "NREIT",
     "security_type": "REIT",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-04",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Access Bank Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "FirstTrust Mortgage Bank Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "NASD Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Nitrox Industrial Gases Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Oil and Gas",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "McNichols Consolidated Plc",
     "ticker": "MCNICHOLS",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Growth Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-26",
     "registrar_as_recorded": "Coronation Registrars Limited"
    },
    {
     "company": "Ronchess Global Resources Plc",
     "ticker": "RONCHESS",
     "security_type": "Equity",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Growth Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2025-04-02",
     "registrar_as_recorded": "Coronation Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://crlselfservice.coronation.ng/faq",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47443_CAVERTON_OFFSHORE_SUPPORT_GROUP_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2025_FINANCIAL_STATEMENTS_JULY_2026.pdf",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://www.coronation.ng/customer-complaints-management---coronation-registrars/",
    "https://shareholderlive.coronationregistrars.com/udivsearch/",
    "https://doclib.ngxgroup.com/Listings-site/corporate-disclosure-site/Documents/CAVERTON_NOTICE_OF_ANNUAL_GENERAL_MEETING_.pdf",
    "https://www.coronation.ng/contact-us/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Number variant: No. 10 Amodu Ojikutu on the unclaimed-dividend page and in Caverton's AGM notice (31 Oct 2025); one building (group site: Coronation Plaza, 9-12). Workstation: Website redirects to coronation.ng. Abuja and Port Harcourt addresses on the group contact page appear under other group companies; they are listed in the offices table as group company offices, not registrar offices. SEC register shows fidelity bond expiry January 31, 2026, which is past. Netcup: SEC register shows fidelity bond expiry 31 Jan 2026 (past) while others show 31 Dec 2026: worth asking SEC. SEC lists a mobile number and a legal-desk email."
  },
  {
   "slug": "cardinalstone",
   "display_name": "CardinalStone",
   "legal_name": "CardinalStone Registrars Ltd.",
   "trading_name": "CardinalStone Registrars",
   "names_in_mapping_file": [
    "CardinalStone Registrars Ltd."
   ],
   "priority": "in scope",
   "website": {
    "url": "https://cardinalstoneregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "registrars@cardinalstone.com",
   "primary_phone": "+2342017120090",
   "emails": [
    {
     "address": "registrars@cardinalstone.com",
     "label": "general; obfuscated on website, plain on SEC register",
     "sources": [
      "SEC register",
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2342017120090",
     "range_end": null,
     "as_printed": "+234 201 7120 090",
     "label": "Lagos office",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2342016308091",
     "range_end": null,
     "as_printed": "+234 201 6308 091",
     "label": "Lagos office",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2348073580521",
     "range_end": null,
     "as_printed": "08073580521",
     "label": "forfeited/unclaimed dividend enquiries (FAQ)",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "335/337 Herbert Macaulay Way, Yaba, Lagos",
    "city": "Yaba",
    "state": "Lagos",
    "confidence": "High",
    "flag": "CONFLICT"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "335/337 Herbert Macaulay Way, Yaba, Lagos",
     "city_state": "Lagos",
     "phone": "+234 201 7120 090; +234 201 6308 091",
     "email": "registrars@cardinalstone.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://cardinalstoneregistrars.com/contact-us-2/",
     "show_on_page": true,
     "note": "HQ flag CONFLICT."
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "Plot 252 Herbert Macaulay Way, Central Business District, Abuja (FCMB Building per e-dividend form)",
     "city_state": "Abuja, FCT",
     "phone": "+234 908 182 8746",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cardinalstoneregistrars.com/contact-us-2/",
     "show_on_page": true,
     "note": "Building named as FCMB Building in https://cardinalstoneregistrars.com/vrs/E-dividend-Mandate-Form.pdf"
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "85 Aba Road, by Garrison Junction, Port Harcourt, Rivers (FCMB Building per e-dividend form)",
     "city_state": "Port Harcourt, Rivers",
     "phone": "+234 903 450 1565",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cardinalstoneregistrars.com/contact-us-2/",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (CardinalStone Partners)",
     "address": "5 Okotie Eboh Street, Ikoyi, Lagos",
     "city_state": "Lagos",
     "phone": "+234 201 631 2225",
     "email": null,
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://cardinalstone.com/registrar-services/",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (CardinalStone Partners)",
     "address": "4 Misratah Street, Wuse II, Abuja",
     "city_state": "Abuja, FCT",
     "phone": null,
     "email": null,
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://cardinalstone.com/registrar-services/",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://shareholders.cardinalstone.com",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://e-dividend.cardinalstone.com",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://vrss.cardinalstone.com/emandate.html",
     "description": "e-dividend mandate",
     "status": "reported by one research run, not re-confirmed",
     "safe_to_link": false
    }
   ],
   "parent_group": "Acquired by CardinalStone Partners in April 2013 (website); email uses the group domain",
   "latest_operating_evidence": "2026-10-15 Guinea Insurance Plc: https://doclib.ngxgroup.com/Financial_NewsDocs/48354_GUINEA_INSURANCE_PLC.-AGM_NOTICE__CORPORATE_ACTIONS_NOVEMBER_2026.pdf",
   "client_count": 16,
   "clients": [
    {
     "company": "FCMB Group Plc",
     "ticker": "FCMB",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2025-12-08 (EGM date; notice undated)",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Guinea Insurance Plc",
     "ticker": "GUINEAINS",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-10-15",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "HBM Nigeria Plc",
     "ticker": "HBMNG",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Premium Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-07-28",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Livestock Feeds Plc",
     "ticker": "LIVESTOCK",
     "security_type": "Equity",
     "sector": "AGRICULTURE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Morison Industries Plc",
     "ticker": "MORISON",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-04-21",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Nigerian Aviation Handling Company Plc",
     "ticker": "NAHCO",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-30",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "NPF Microfinance Bank Plc",
     "ticker": "NPFMCRFBK",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-08-19",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Premier Paints Plc",
     "ticker": "PREMPAINTS",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-07",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "The Okomu Oil Palm Company Plc",
     "ticker": "OKOMUOIL",
     "security_type": "Equity",
     "sector": "AGRICULTURE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-27",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "TotalEnergies Marketing Nigeria Plc",
     "ticker": "TOTAL",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-05-15",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Trans-Nationwide Express Plc",
     "ticker": "TRANSEXPR",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-24",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Acorn Petroleum Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Oil and Gas",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "AG Mortgage Bank Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Infrastructure Credit Guarantee Company",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Purple Real Estate Income PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Real Estate",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    },
    {
     "company": "Royal Exchange Plc",
     "ticker": "ROYALEX",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-07",
     "registrar_as_recorded": "CardinalStone Registrars Ltd."
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://cardinalstoneregistrars.com/contact-us-2",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/46703_TRANS-NATIONWIDE_EXPRESS_PLC.-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_APRIL_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47008_TOTALENERGIES_MARKETING_NIGERIA_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_MAY_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47222_ROYAL_EXCHANGE_PLC.-_NOTICES_OF_EXTRA-ORDINARY_GENERAL_MEETING_(EGM)_-__EXTRA-ORDINARY_GENERAL_MEETING_(EGM)_JUNE_2026.pdf",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://cardinalstoneregistrars.com/faq/",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/46600_ROYAL_EXCHANGE_PLC.-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_APRIL_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48234_ROYAL_EXCHANGE_PLC.-_QUARTER_3_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_OCTOBER_2026.pdf",
    "https://icmr.org.ng/cardinalstone-registrars-limited/",
    "https://cardinalstoneregistrars.com/contact-us-2/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Several Royal Exchange filings print 358 Herbert Macaulay instead of 335/337; no relocation notice found, so likely a client typing error (unconfirmed). SEC register phone '+234 712 0090' looks incomplete. Netcup: Shares email domain with parent group (cardinalstone.com)."
  },
  {
   "slug": "apel",
   "display_name": "Apel",
   "legal_name": "Apel Registrars And Corporate Services Limited",
   "trading_name": "Apel Capital Registrars",
   "names_in_mapping_file": [
    "Apel Registrars And Corporate Services Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://www.apel.com.ng",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@apel.com.ng",
   "primary_phone": "+2347046126698",
   "emails": [
    {
     "address": "registrars@apel.com.ng",
     "label": "registrars desk",
     "sources": [
      "SEC register"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "info@apel.com.ng",
     "label": "general",
     "sources": [
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "customercare@apel.ng",
     "label": "customer care; link target. Visible text reads 'customercare@apelng'",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "registrars@apel.ng",
     "label": "general (own site)",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2347046277071",
     "range_end": null,
     "as_printed": "+234 704 627 7071",
     "label": "main line / WhatsApp",
     "type": "whatsapp",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2347046126698",
     "range_end": null,
     "as_printed": "07046126698",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+2348128225828",
     "range_end": null,
     "as_printed": "08128225828",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "8 Alhaji Bashorun Street, off Norman Williams Crescent, South-West Ikoyi, Lagos",
    "city": "Ikoyi",
    "state": "Lagos",
    "confidence": "Medium",
    "flag": "CONFLICT"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "8 Alhaji Bashorun Street, off Norman Williams Crescent, South-West Ikoyi, Lagos",
     "city_state": "Lagos",
     "phone": "+234 704 612 6698",
     "email": "registrars@apel.ng",
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
     "show_on_page": true,
     "note": "HQ flag CONFLICT."
    }
   ],
   "portals": [
    {
     "url": "https://myapel.com",
     "description": "shareholder portal, named in FAQ",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://registrars.apel.com.ng/",
     "description": "KYC Update, E-dividend Search",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Apel Asset group",
   "latest_operating_evidence": "2026-11-09: Eunisell Interlinked AGM notice on NGX names Apel as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/48379_EUNISELL_INTERLINKED_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_NOVEMBER_2026.pdf)",
   "client_count": 12,
   "clients": [
    {
     "company": "International Breweries Plc",
     "ticker": "INTBREW",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-02",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Lasaco Assurance Plc",
     "ticker": "LASACO",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-10",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Linkage Assurance Plc",
     "ticker": "LINKASSURE",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-05",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Mutual Benefits Assurance Plc",
     "ticker": "MBENEFIT",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-02",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "NCR",
     "ticker": "NCR",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-18",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "NEM Insurance Plc",
     "ticker": "NEM",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-01",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Red Star Express Plc",
     "ticker": "REDSTAREX",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-06-30",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Skyway Aviation Handling Company Plc",
     "ticker": "SKYAVN",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-10",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "The Initiates Plc",
     "ticker": "TIP",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Growth Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-07-30",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Mass Telecoms Innovation Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Telecommunication",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Eunisell Interlinked Plc",
     "ticker": "EUNISELL",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-11-09",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    },
    {
     "company": "Pharma-Deko Plc",
     "ticker": "PHARMDEKO",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2022-05-17",
     "registrar_as_recorded": "Apel Registrars And Corporate Services Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48379_EUNISELL_INTERLINKED_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_NOVEMBER_2026.pdf",
    "https://icmr.org.ng/apel-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47950_EUNISELL_INTERLINKED_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_SEPTEMBER_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47444_INTERNATIONAL_BREWERIES_PLC.-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_JULY_2026.pdf",
    "https://registrars.apel.com.ng/contact",
    "https://icmr.org.ng/apel-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Registrar website says No. 6; SEC register, ICMR and the 9 Nov 2026 Eunisell notice say No. 8. Newest dated primary source used. Street/crescent wording also varies. Netcup: Name change from Apel Capital Registrars announced on LinkedIn (Oct 2026, seen via search index); some clients still use the old name. Sister site shows a malformed email 'customercare@apelng': not recorded."
  },
  {
   "slug": "cordros",
   "display_name": "Cordros",
   "legal_name": "Cordros Registrars Limited",
   "trading_name": "Cordros Registrars",
   "names_in_mapping_file": [
    "Cordros Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://cordros.com/registrars",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "contactcentre@cordros.com",
   "primary_phone": "+2347002673767",
   "emails": [
    {
     "address": "contactcentre@cordros.com",
     "label": "contact centre",
     "sources": [
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "cordrosregistrars@cordros.com",
     "label": "registrar desk",
     "sources": [
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "registrars@cordros.com",
     "label": "registrar desk",
     "sources": [
      "ICMR directory"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "compliance@cordros.com",
     "label": "compliance, as on SEC register",
     "sources": [
      "SEC register"
     ],
     "show_on_page": false,
     "reason_if_hidden": "compliance desk"
    }
   ],
   "phones": [
    {
     "e164": "+2347002673767",
     "range_end": null,
     "as_printed": "+234 700 267 3767 (0700 CORDROS)",
     "label": "contact centre",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+2342012910538",
     "range_end": null,
     "as_printed": "+234 201 291 0538",
     "label": "WhatsApp",
     "type": "whatsapp",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+23419049041",
     "range_end": null,
     "as_printed": "019049041",
     "label": "main phone on SEC register",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "131 Ikorodu Road, Onipanu, Lagos",
    "city": "Onipanu",
    "state": "Lagos",
    "confidence": "Medium",
    "flag": "CONFLICT"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "131 Ikorodu Road, Onipanu, Lagos",
     "city_state": "Lagos",
     "phone": "0700 CORDROS",
     "email": "contactcentre@cordros.com",
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cordros.com/registrars/contact-us",
     "show_on_page": true,
     "note": "HQ flag CONFLICT."
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "21, 70, 110 Norman Williams Street, Ikoyi, Lagos",
     "city_state": "Lagos",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cordros.com/registrars/contact-us",
     "show_on_page": true,
     "note": "Own site 'Lagos Island'; SEC gives No. 21 as the address"
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "2 Aba Close, off Ogbomosho Street, Area 8, Garki, Abuja",
     "city_state": "Abuja, FCT",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cordros.com/registrars/contact-us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Shareholder service point (in partner bank)",
     "is_head_office": false,
     "belongs_to": "registrar desk in Globus Bank",
     "address": "Globus Bank, Plot 467 Trans-Amadi Layout, Port Harcourt, Rivers",
     "city_state": "Port Harcourt, Rivers",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cordros.com/registrars/contact-us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Shareholder service point (in partner bank)",
     "is_head_office": false,
     "belongs_to": "registrar desk in Globus Bank",
     "address": "Globus Bank, 11A Murtala Muhammad Way, Kano",
     "city_state": "Kano, Kano",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://cordros.com/registrars/contact-us",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://cordros.com/registrars",
     "description": "Claim Dividend, Dematerialization, Check Unclaimed Dividends links",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Subsidiary of Cordros Capital",
   "latest_operating_evidence": "2026-10-21: Ava Capital Q3 2026 statement on NGX names Cordros; Eterna appointed Cordros from 1 Aug 2026 (https://doclib.ngxgroup.com/Financial_NewsDocs/47804_ETERNA_PLC.-NOTICE_OF_CHANGE_OF_REGISTRARS_CORPORATE_ACTIONS_AUGUST_2026.pdf)",
   "client_count": 8,
   "clients": [
    {
     "company": "AVA Infrastructure Fund",
     "ticker": "AVAIF",
     "security_type": "Fund",
     "sector": "CONSTRUCTION/REAL ESTATE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-03-31 (period end of Q1 2026 report)",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "CWG Plc",
     "ticker": "CWG",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-23",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "Ellah Lakes Plc",
     "ticker": "ELLAHLAKES",
     "security_type": "Equity",
     "sector": "AGRICULTURE",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-26",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "Eterna Plc",
     "ticker": "ETERNA",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-08-13",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "Mecure Industries Plc",
     "ticker": "MECURE",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Growth Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-02-26",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "Capital Hotels Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Hospitality",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "Ava Capital Plc",
     "ticker": "AVACAP",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-10-21",
     "registrar_as_recorded": "Cordros Registrars Limited"
    },
    {
     "company": "C & I Leasing Plc",
     "ticker": "CILEASING",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-05-18",
     "registrar_as_recorded": "Cordros Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://eternaplc.com/wp-content/uploads/2026/08/Appointment-of-Cordros-Registrars-Limited-as-Registrar.pdf",
    "https://cordros.com/contact-us",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48111_AVA_CAPITAL_PLC-_QUARTER_3_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_OCTOBER_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47023_C_AND_I_LEASING_PLC.-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_MAY_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47804_ETERNA_PLC.-NOTICE_OF_CHANGE_OF_REGISTRARS_CORPORATE_ACTIONS_AUGUST_2026.pdf",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292006228G0L6U0I659",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47016_C_AND_I_LEASING_PLC.-CORPORATE_ACTIONS_ANNOUNCEMENT_CORPORATE_ACTIONS_MAY_2026.pdf",
    "https://icmr.org.ng/cordros-registrars-limited/",
    "https://cordros.com/registrars/contact-us"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Two live addresses. Newest dated primary evidence (Eterna 13 Aug 2026, AVA Capital 21 Oct 2026, C&I Leasing AGM May 2026) gives 131 Ikorodu Road. SEC register and a C&I Leasing corporate action (May 2026) give 21 Norman Williams Street; ICMR gives No. 70. No relocation notice found. Confirm before posting documents. www.cordros.com showed a Cloudflare DNS error; cordros.com works. Netcup: Port Harcourt and Kano points are inside Globus Bank branches; type recorded as service points, not registrar-owned branches."
  },
  {
   "slug": "carnation",
   "display_name": "Carnation",
   "legal_name": "Carnation Registrars Limited",
   "trading_name": "Carnation Registrars",
   "names_in_mapping_file": [
    "Carnation Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://carnationregistrars.com",
    "safe_to_link": false,
    "problem": "security certificate does not match the domain"
   },
   "primary_email": "info@carnationregistrars.com",
   "primary_phone": "+2348107005494",
   "emails": [
    {
     "address": "info@carnationregistrars.com",
     "label": "general",
     "sources": [
      "SEC register",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2348107005494",
     "range_end": null,
     "as_printed": "08107005494",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "2A Gbagada Expressway, Anthony, Lagos (Beko Ransome Kuti Gardens, opposite Dr Anthony)",
    "city": "Anthony",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "2A Gbagada Expressway, Anthony, Lagos (Beko Ransome Kuti Gardens, opposite Dr Anthony)",
     "city_state": "Lagos",
     "phone": "+234 810 700 5494",
     "email": "info@carnationregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [],
   "parent_group": null,
   "latest_operating_evidence": "2026-09-07: Omatek Ventures AGM notice on NGX names Carnation as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/47887_OMATEK_VENTURES_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_SEPTEMBER_2026.pdf)",
   "client_count": 6,
   "clients": [
    {
     "company": "African Alliance Insurance Plc",
     "ticker": "AFRINSURE",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "c. 2023-06 (notice undated; AGM held 2023-12-15)",
     "registrar_as_recorded": "Carnation Registrars Limited"
    },
    {
     "company": "Multiverse Mining and Exploration Plc",
     "ticker": "MULTIVERSE",
     "security_type": "Equity",
     "sector": "NATURAL RESOURCES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-08",
     "registrar_as_recorded": "Carnation Registrars Limited"
    },
    {
     "company": "Universal Insurance Plc",
     "ticker": "UNIVINSURE",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-05",
     "registrar_as_recorded": "Carnation Registrars Limited"
    },
    {
     "company": "Riggs Ventures West African PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Industrials",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Carnation Registrars Limited"
    },
    {
     "company": "Golden Guinea Breweries Plc",
     "ticker": "GOLDBREW",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-08-02",
     "registrar_as_recorded": "Carnation Registrars Limited"
    },
    {
     "company": "Omatek Ventures Plc",
     "ticker": "OMATEK",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-07",
     "registrar_as_recorded": "Carnation Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://icmr.org.ng/carnation-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47887_OMATEK_VENTURES_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_SEPTEMBER_2026.pdf",
    "https://icmr.org.ng/carnation-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Website certificate names a different host (*.web-hosting.com); not bypassed. Same result as the Netcup run. Second address source is the undated ICMR directory. A search summary of the site lists +234 813 039 3743 as well; not verified, not recorded. Netcup: Website needs human check in a normal browser (certificate problem may be on their side)."
  },
  {
   "slug": "datamax",
   "display_name": "DataMax",
   "legal_name": "DataMax Registrars Limited",
   "trading_name": "DataMax Registrars",
   "names_in_mapping_file": [
    "DataMax Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://datamaxregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "datamax@datamaxregistrars.com",
   "primary_phone": "+2347064000751",
   "emails": [
    {
     "address": "datamax@datamaxregistrars.com",
     "label": "general; obfuscated on website, plain on SEC register",
     "sources": [
      "SEC register",
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "investorsenquiries@datamaxregistrars.com",
     "label": "investor enquiries (GTCO circular)",
     "sources": [
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "RMU@datamaxregistrars.com",
     "label": "register management unit (GTCO circular)",
     "sources": [
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2347064000751",
     "range_end": null,
     "as_printed": "07064000751",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register",
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "2C Gbagada Expressway, by Beko Ransome Kuti Park, Gbagada, Lagos",
    "city": "Gbagada",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "2C Gbagada Expressway, by Beko Ransome Kuti Park, Gbagada, Lagos",
     "city_state": "Lagos",
     "phone": "+234 706 400 0751",
     "email": "datamax@datamaxregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://datamaxregistrars.com/?page_id=677",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://dataregview.datamaxregistrars.info",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://datamaxregistrars.com/",
     "description": "Shareholder Portal, e-Contact Update, e-Dividend menu items",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": null,
   "latest_operating_evidence": "2026-10-29: Seplat Q3 2026 interim dividend notice on NGX names DataMax as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/48221_SEPLAT_ENERGY_PLC-ANNOUNCEMENT_ON_Q3_2026_INTERIM_DIVIDEND_CORPORATE_ACTIONS_OCTOBER_2026.pdf)",
   "client_count": 6,
   "clients": [
    {
     "company": "AXA Mansard Insurance Plc",
     "ticker": "MANSARD",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-01",
     "registrar_as_recorded": "DataMax Registrars Limited"
    },
    {
     "company": "Legend Internet Plc",
     "ticker": "LEGENDINT",
     "security_type": "Equity",
     "sector": "ICT",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "2025-10-20",
     "registrar_as_recorded": "DataMax Registrars Limited"
    },
    {
     "company": "Nigerian Exchange Group Plc",
     "ticker": "NGXGROUP",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-27",
     "registrar_as_recorded": "DataMax Registrars Limited"
    },
    {
     "company": "Seplat Energy Plc",
     "ticker": "SEPLAT",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-29",
     "registrar_as_recorded": "DataMax Registrars Limited"
    },
    {
     "company": "Zichis Agro Allied Industries Plc",
     "ticker": "ZICHIS",
     "security_type": "Equity",
     "sector": "AGRICULTURE",
     "board": "Growth Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026 (FY2025 accounts; exact date not in notes)",
     "registrar_as_recorded": "DataMax Registrars Limited"
    },
    {
     "company": "Guaranty Trust Holding Company Plc",
     "ticker": "GTCO",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-28",
     "registrar_as_recorded": "DataMax Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://datamaxregistrars.com",
    "https://icmr.org.ng/datamax-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://datamaxregistrars.com/?page_id=677",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/Seplat_Energy_Plc_2025_AFS.pdf",
    "https://doclib.ngxgroup.com/Listings-site/corporate-disclosure-site/Documents/GTCO_EXPLANATORY_CIRCULAR_CANCELLATION_OF_GDR_.pdf",
    "https://lei.bloomberg.com/leis/view/984500C179T541U2E169",
    "https://icmr.org.ng/datamax-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": ""
  },
  {
   "slug": "pace",
   "display_name": "Pace",
   "legal_name": "Pace Registrars Ltd",
   "trading_name": "Pace Registrars",
   "names_in_mapping_file": [
    "Pace Registrars Ltd"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://paceregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@paceregistrars.com",
   "primary_phone": "+2347072427755",
   "emails": [
    {
     "address": "info@paceregistrars.com",
     "label": "general",
     "sources": [
      "SEC register",
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2347072427755",
     "range_end": null,
     "as_printed": "07072427755",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412790797",
     "range_end": null,
     "as_printed": "01-2790797-8/ 9",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+23412635607",
     "range_end": null,
     "as_printed": "01-2635607, 01-7303445, 01-2805538",
     "label": "lines printed by client",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+23417303445",
     "range_end": null,
     "as_printed": "01-2635607, 01-7303445, 01-2805538",
     "label": "lines printed by client",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+23412805538",
     "range_end": null,
     "as_printed": "01-2635607, 01-7303445, 01-2805538",
     "label": "lines printed by client",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "8th Floor, Knight Frank Building, 24 Campbell Street, Lagos Island, Lagos",
    "city": "Lagos Island",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "8th Floor, Knight Frank Building, 24 Campbell Street, Lagos Island, Lagos",
     "city_state": "Lagos",
     "phone": "+234 707 242 7755",
     "email": "info@paceregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.paceregistrars.com/contact.php",
     "show_on_page": true,
     "note": "Sterling HoldCo notice (15 May 2026) calls the same 8th-floor address Akuro House."
    },
    {
     "type": "Shareholder service point (client's bank)",
     "is_head_office": false,
     "belongs_to": "client's bank branches",
     "address": "Any Sterling Bank or Alternative Bank branch (forms for Sterling HoldCo shareholders)",
     "city_state": "Nationwide",
     "phone": null,
     "email": null,
     "confidence": "Low",
     "date": "2026-05-15",
     "source": "https://doclib.ngxgroup.com/Financial_NewsDocs/Sterling_HoldCo_-_Notice_of_the_3rd_Annual_General_Meeting.pdf",
     "show_on_page": true,
     "note": "Applies to Sterling HoldCo forms only, per the AGM notice"
    }
   ],
   "portals": [],
   "parent_group": null,
   "latest_operating_evidence": "2026-07-14: Japaul Gold AGM notice on NGX names Pace (Stage 1, scanned PDF read visually)",
   "client_count": 4,
   "clients": [
    {
     "company": "Academy Press Plc",
     "ticker": "ACADEMY",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-06-30",
     "registrar_as_recorded": "Pace Registrars Ltd"
    },
    {
     "company": "SFS Real Estate Investment Trust",
     "ticker": "SFSREIT",
     "security_type": "REIT",
     "sector": "Construction/Real Estate",
     "board": "Real Estate Investment Trust & Close End Fund",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-26",
     "registrar_as_recorded": "Pace Registrars Ltd"
    },
    {
     "company": "Sterling Financial Holdings Company Plc",
     "ticker": "STERLINGNG",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-05-15",
     "registrar_as_recorded": "Pace Registrars Ltd"
    },
    {
     "company": "Japaul Gold & Ventures Plc",
     "ticker": "JAPAULGOLD",
     "security_type": "Equity",
     "sector": "OIL AND GAS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-14",
     "registrar_as_recorded": "Pace Registrars Ltd"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=2",
    "https://paceregistrars.com/contact.php",
    "https://icmr.org.ng/pace-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?page=2&query=registrars",
    "https://www.paceregistrars.com/contact.php",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47375_ACADEMY_PRESS_PLC.-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_JULY_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/Sterling_HoldCo_-_Notice_of_the_3rd_Annual_General_Meeting.pdf",
    "https://icmr.org.ng/pace-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Sterling HoldCo notice (15 May 2026) calls the same 8th-floor address Akuro House. Workstation: Website footer is dated 2021; contact page answered HTTP 409 while still showing content. Not the same company as PAC Registrars."
  },
  {
   "slug": "veritas",
   "display_name": "Veritas",
   "legal_name": "Veritas Registrars Limited",
   "trading_name": "Veritas Registrars",
   "names_in_mapping_file": [
    "Veritas Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://veritasregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "enquiry@veritasregistrars.com",
   "primary_phone": "+2342012784167",
   "emails": [
    {
     "address": "enquiry@veritasregistrars.com",
     "label": "enquiries",
     "sources": [
      "SEC register",
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "customercare@veritasregistrars.com",
     "label": "customer care",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "probateadministration@veritasregistrars.com",
     "label": "probate / transmission",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "vrcustomerservice@veritasregistrars.com",
     "label": "change of name / customer service",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2342012784167",
     "range_end": null,
     "as_printed": "+234 02 01 278 4167",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2342012784169",
     "range_end": null,
     "as_printed": "+234 02 01 278 4169",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2342012784170",
     "range_end": null,
     "as_printed": "+234 02 01 278 4170",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2347044997048",
     "range_end": null,
     "as_printed": "+234 704 499 7048",
     "label": "text messages only",
     "type": "sms_only",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412784158",
     "range_end": null,
     "as_printed": "01-2784158, 01-2784172 (probate); 01-2784156 (customer service)",
     "label": "department lines (FAQ)",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412784172",
     "range_end": null,
     "as_printed": "01-2784158, 01-2784172 (probate); 01-2784156 (customer service)",
     "label": "department lines (FAQ)",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412784156",
     "range_end": null,
     "as_printed": "01-2784158, 01-2784172 (probate); 01-2784156 (customer service)",
     "label": "department lines (FAQ)",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+23412708930",
     "range_end": "8934",
     "as_printed": "234-1-2708930-4",
     "label": "line printed by client",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "Plot 89A Ajose Adeogun Street, Victoria Island, Lagos",
    "city": "Victoria Island",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "Plot 89A Ajose Adeogun Street, Victoria Island, Lagos",
     "city_state": "Lagos",
     "phone": "+234 201 278 4167/4169/4170",
     "email": "enquiry@veritasregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.veritasregistrars.com/ContactUs.aspx",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Liaison office",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "40 Aba Road, CFC Bus Stop, Port Harcourt, Rivers State",
     "city_state": "Port Harcourt, Rivers",
     "phone": "+234 704 222 6234 (0704 222 6234)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.veritasregistrars.com/ContactUs.aspx",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Liaison office",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "57 Gana Street, Maitama, Abuja, FCT",
     "city_state": "Abuja, FCT",
     "phone": "+234 9 291 5070 (09-2915070; site also writes 0209 291 5070)",
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.veritasregistrars.com/ContactUs.aspx",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Shareholder service point (bank branches)",
     "is_head_office": false,
     "belongs_to": "Zenith Bank branches",
     "address": "Any Zenith Bank branch ('walk into any Zenith Bank branch', own contact page)",
     "city_state": "Nationwide",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.veritasregistrars.com/ContactUs.aspx",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://veritasregistrars.com/UnclaimedDividends.aspx",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": "https://www.veritasregistrars.com/",
     "description": "online portal link 'Customer Services' / 'Unclaimed Dividends'",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Formerly Zenith Registrars; site cites a partnership with Zenith Bank",
   "latest_operating_evidence": "2026-10-21: Guinness Nigeria interim dividend notice on NGX names Veritas as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/48116_GUINNESS_NIGERIA_PLC-GUINNESS_NIGERIA_PLC_-_Q3F26_INTERIM_DIVIDENDS_CORPORATE_ACTIONS_OCTOBER_2026.pdf)",
   "client_count": 4,
   "clients": [
    {
     "company": "Dangote Sugar Refinery Plc",
     "ticker": "DANGSUGAR",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-09-24",
     "registrar_as_recorded": "Veritas Registrars Limited"
    },
    {
     "company": "Guinness Nigeria Plc",
     "ticker": "GUINNESS",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-21",
     "registrar_as_recorded": "Veritas Registrars Limited"
    },
    {
     "company": "May & Baker Nigeria Plc",
     "ticker": "MAYBAKER",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-03-26",
     "registrar_as_recorded": "Veritas Registrars Limited"
    },
    {
     "company": "Zenith Bank Plc",
     "ticker": "ZENITHBANK",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Premium Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-04-10",
     "registrar_as_recorded": "Veritas Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=2",
    "https://veritasregistrars.com/ContactUs.aspx",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/48116_GUINNESS_NIGERIA_PLC-GUINNESS_NIGERIA_PLC_-_Q3F26_INTERIM_DIVIDENDS_CORPORATE_ACTIONS_OCTOBER_2026.pdf",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/46630_ZENITH_BANK_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_APRIL_2026.pdf",
    "https://icmr.org.ng/veritas-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?page=2&query=registrars",
    "https://www.veritasregistrars.com/ContactUs.aspx",
    "https://doclib.ngxgroup.com/Listings-site/corporate-disclosure-site/Documents/Guinness_Nigeria_-_Audited_Financial_Statement.pdf",
    "https://icmr.org.ng/veritas-registrars-limited/",
    "https://www.veritasregistrars.com/FAQs.aspx",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47520_GUINNESS_NIG_PLC-GUINNESS_NIGERIA_PLC_-_INTERIM_DIVIDEND_ANNOUNCEMENT_CORPORATE_ACTIONS_JULY_2026.pdf"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": ""
  },
  {
   "slug": "crescent",
   "display_name": "Crescent",
   "legal_name": "Crescent Registrars Limited",
   "trading_name": "Crescent Registrars",
   "names_in_mapping_file": [
    "Crescent Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://crescentregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@crescentregistrars.com",
   "primary_phone": "+2348054538356",
   "emails": [
    {
     "address": "info@crescentregistrars.com",
     "label": "general",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "allcrlfinance@crescentregistrars.com",
     "label": "as on SEC register; looks like a finance mailbox",
     "sources": [
      "SEC register"
     ],
     "show_on_page": false,
     "reason_if_hidden": "finance desk"
    }
   ],
   "phones": [
    {
     "e164": "+234204538671",
     "range_end": null,
     "as_printed": "020-4538671-4",
     "label": "head office",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": "unusual number length as printed (020-4538671-4); confirm before publishing"
    },
    {
     "e164": "+2348054538356",
     "range_end": null,
     "as_printed": "08054538356",
     "label": "main line on SEC register",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "23 Olusoji Idowu Street, Ilupeju, Lagos (behind Mutual Benefit Insurance head office)",
    "city": "Ilupeju",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "23 Olusoji Idowu Street, Ilupeju, Lagos (behind Mutual Benefit Insurance head office)",
     "city_state": "Lagos",
     "phone": "020-4538671-4",
     "email": "info@crescentregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://crescentregistrars.com/Contact/",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "Suite 26, Amssco Plaza, Niger River Road, Amssco Platinum City Estate, Galadimawa, Abuja",
     "city_state": "Abuja, FCT",
     "phone": null,
     "email": null,
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://crescentregistrars.com/Contact/",
     "show_on_page": true,
     "note": "Relocated per homepage notice (undated)"
    }
   ],
   "portals": [
    {
     "url": "https://crescentregistrars.com/Login/Company",
     "description": null,
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    },
    {
     "url": null,
     "description": "sharesMobile app (named on homepage; no store link found)",
     "status": "app named, no link found",
     "safe_to_link": false
    }
   ],
   "parent_group": "Formerly Oceanic Registrars",
   "latest_operating_evidence": "2026-07-29 Sunu Assurances Nigeria Plc: https://doclib.ngxgroup.com/Financial_NewsDocs/44138_SUNU_ASSURANCES_NIGERIA_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_MAY_2025.pdf",
   "client_count": 3,
   "clients": [
    {
     "company": "Afromedia Plc",
     "ticker": "AFROMEDIA",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2021-11-23",
     "registrar_as_recorded": "Crescent Registrars Limited"
    },
    {
     "company": "Cutix Plc",
     "ticker": "CUTIX",
     "security_type": "Equity",
     "sector": "INDUSTRIAL GOODS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2022-06-23",
     "registrar_as_recorded": "Crescent Registrars Limited"
    },
    {
     "company": "Sunu Assurances Nigeria Plc",
     "ticker": "SUNUASSUR",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-07-29",
     "registrar_as_recorded": "Crescent Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://crescentregistrars.com/Contact",
    "https://icmr.org.ng/crescent-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://crescentregistrars.com/Contact/",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47634_SUNU_ASSURANCES_NIGERIA_PLC-CORPORATE_ANNOUNCEMENT_CORPORATE_ACTIONS_JULY_2026.pdf",
    "https://icmr.org.ng/crescent-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": ""
  },
  {
   "slug": "lighthouse",
   "display_name": "Lighthouse",
   "legal_name": "Lighthouse Registrars Ltd",
   "trading_name": "Lighthouse Registrars",
   "names_in_mapping_file": [
    "Lighthouse Registrars Ltd"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://lighthousecapital.ng",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@lighthousecapital.ng",
   "primary_phone": "+2342012718910",
   "emails": [
    {
     "address": "info.reg@lighthousecapital.ng",
     "label": "registrar desk",
     "sources": [
      "SEC register"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "info@lighthousecapital.ng",
     "label": "group general",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "lighthouseRegistrars@lighthouse.com.ng",
     "label": "registrar (client notice; different domain lighthouse.com.ng)",
     "sources": [
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2342012718910",
     "range_end": null,
     "as_printed": "0201 271 8910",
     "label": "group line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2349090908084",
     "range_end": null,
     "as_printed": "0909-090-8084",
     "label": "group line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2349090908085",
     "range_end": null,
     "as_printed": "0909-090-8085",
     "label": "group line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "2nd Floor, 39 Adeola Odeku Street, Victoria Island, Lagos",
    "city": "Victoria Island",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "2nd Floor, 39 Adeola Odeku Street, Victoria Island, Lagos",
     "city_state": "Lagos",
     "phone": "+234 1 271 8910",
     "email": "info.reg@lighthousecapital.ng",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (Lighthouse Group)",
     "address": "16th Floor, World Trade Center, 1113 Constitution Avenue, Central Business District, Abuja",
     "city_state": "Abuja, FCT",
     "phone": null,
     "email": null,
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://lighthousecapital.ng/subsidiaries/lighthouse-registrars",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (Lighthouse Group)",
     "address": "UBA House, 3 Yakubu Gowon Way, Kaduna",
     "city_state": "Kaduna, Kaduna",
     "phone": null,
     "email": null,
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://lighthousecapital.ng/subsidiaries/lighthouse-registrars",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [],
   "parent_group": "Lighthouse Capital group; website, domain and Lagos address are shared",
   "latest_operating_evidence": "2026-06-17: Cornerstone Insurance dividend notice on NGX names Lighthouse as registrar (https://doclib.ngxgroup.com/Financial_NewsDocs/47198_CORNERSTONE_INSURANCE_PLC-DIVIDEND_ANNOUNCEMENT_CORPORATE_ACTIONS_JUNE_2026.pdf)",
   "client_count": 3,
   "clients": [
    {
     "company": "Cornerstone Insurance Plc",
     "ticker": "CORNERST",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-06-17",
     "registrar_as_recorded": "Lighthouse Registrars Ltd"
    },
    {
     "company": "Capital Bancorp PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Lighthouse Registrars Ltd"
    },
    {
     "company": "Lighthouse Financial Services Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Financial Services",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Lighthouse Registrars Ltd"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://lighthousecapital.ng/contact-us",
    "https://icmr.org.ng/lighthouse-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47198_CORNERSTONE_INSURANCE_PLC-DIVIDEND_ANNOUNCEMENT_CORPORATE_ACTIONS_JUNE_2026.pdf",
    "https://lighthousecapital.ng/subsidiaries/lighthouse-registrars",
    "https://icmr.org.ng/lighthouse-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: No separate registrar website found. Netcup: Two email domains in use (lighthousecapital.ng, lighthouse.com.ng)."
  },
  {
   "slug": "pac",
   "display_name": "PAC",
   "legal_name": "PAC Registrars & Investor Services Limited",
   "trading_name": "PAC Registrars",
   "names_in_mapping_file": [
    "PAC Registrars & Investor Services Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://pacregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@pacregistrars.com",
   "primary_phone": "+2349168629450",
   "emails": [
    {
     "address": "info@pacregistrars.com",
     "label": "general",
     "sources": [
      "SEC register",
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2349168629450",
     "range_end": null,
     "as_printed": "+234 916 862 9450",
     "label": "main line (visible text)",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2349086790272",
     "range_end": null,
     "as_printed": "+234 908 679 0272",
     "label": "behind a click-to-call link",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": "SEC register and the registrar's website differ by one digit; confirm before publishing"
    },
    {
     "e164": "+2349080790272",
     "range_end": null,
     "as_printed": "09080790272",
     "label": "main line on SEC register",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": "SEC register and the registrar's website differ by one digit; confirm before publishing"
    }
   ],
   "head_office": {
    "address": "122 Bode Thomas Street, Surulere, Lagos",
    "city": "Surulere",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "122 Bode Thomas Street, Surulere, Lagos",
     "city_state": "Lagos",
     "phone": "+234 916 862 9450",
     "email": "info@pacregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://www.pacregistrars.com/contact",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://shareholder.pacregistrarslimited.com/login.aspx",
     "description": null,
     "status": "address does not resolve (checked 2026-11-27)",
     "safe_to_link": false
    },
    {
     "url": "http://clients.pacregistrarslimited.com/login.aspx",
     "description": null,
     "status": "address does not resolve (checked 2026-11-27)",
     "safe_to_link": false
    },
    {
     "url": "http://brokers.pacregistrarslimited.com/login.aspx",
     "description": null,
     "status": "address does not resolve (checked 2026-11-27)",
     "safe_to_link": false
    },
    {
     "url": "https://docuhub3.nibss-plc.com.ng/edmms/self-service",
     "description": "NIBSS e-dividend mandate",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": "Subsidiary of PanAfrican Capital Holdings",
   "latest_operating_evidence": "2026-10-30: Fortis Global Insurance Q3 2026 statement on NGX names PAC (also PAC replaced First Registrars for Fortis, 9 Dec 2025)",
   "client_count": 3,
   "clients": [
    {
     "company": "Fumman Agricultural Products Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "PAC Registrars & Investor Services Limited"
    },
    {
     "company": "Fortis Global Insurance Plc",
     "ticker": "FTGINSURE",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-30",
     "registrar_as_recorded": "PAC Registrars & Investor Services Limited"
    },
    {
     "company": "Secure Electronic Technology Plc",
     "ticker": "NSLTECH",
     "security_type": "Equity",
     "sector": "SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-08-10",
     "registrar_as_recorded": "PAC Registrars & Investor Services Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://pacregistrars.com/contact",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47794_SECURE_ELECTRONIC_TECHNOLOGY_PLC-_NOTICES_OF_ANNUAL_GENERAL_MEETING_(AGM)_-__ANNUAL_GENERAL_MEETING_(AGM)_AUGUST_2026.pdf",
    "https://icmr.org.ng/pac-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://www.pacregistrars.com/contact",
    "https://icmr.org.ng/pac-registrars-limited/",
    "https://www.pacregistrars.com/register-maintenance"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Shareholder portal domain did not resolve. Three different numbers appear (visible text, link target, SEC register). Not the same company as Pace Registrars. Netcup: Phone on SEC and on own page differ by one digit (0908 079 vs 0908 679): needs a call."
  },
  {
   "slug": "atlas",
   "display_name": "Atlas",
   "legal_name": "Atlas Registrars Limited",
   "trading_name": "Atlas Registrars",
   "names_in_mapping_file": [
    "Atlas Registrars Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://atlasregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "registrars@atlasregistrars.com",
   "primary_phone": "+2348175425054",
   "emails": [
    {
     "address": "registrars@atlasregistrars.com",
     "label": "registrars desk",
     "sources": [
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2348175425054",
     "range_end": null,
     "as_printed": "+234 817 542 5054",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register",
      "registrar or group website"
     ],
     "warning": null
    },
    {
     "e164": "+2348108724445",
     "range_end": null,
     "as_printed": "+234 810 872 4445",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "Bagco Building (4th Floor), 34 Eric Moore Road, Iganmu, Lagos (P.O. Box 3554)",
    "city": "Iganmu",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "Bagco Building (4th Floor), 34 Eric Moore Road, Iganmu, Lagos (P.O. Box 3554)",
     "city_state": "Lagos",
     "phone": "+234 817 542 5054",
     "email": "registrars@atlasregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://atlasregistrars.com/our-contact/",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://docuhub3.nibss-plc.com.ng/edmms/self-service",
     "description": "NIBSS e-dividend mandate, linked from site",
     "status": "address resolves; page function not tested",
     "safe_to_link": true
    }
   ],
   "parent_group": null,
   "latest_operating_evidence": "2026-05-29: Honeywell Flour Mill FY2026 statement on NGX names Atlas (https://doclib.ngxgroup.com/Financial_NewsDocs/47086_HONEYWELL_FLOUR_MILL_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_MAY_2026.pdf); own news post 'Customer Service Week 2026'",
   "client_count": 2,
   "clients": [
    {
     "company": "Honeywell Flour Mill Plc",
     "ticker": "HONYFLOUR",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-05-29",
     "registrar_as_recorded": "Atlas Registrars Limited"
    },
    {
     "company": "Northern Nigeria Flour Mills Plc",
     "ticker": "NNFM",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2023-08-09",
     "registrar_as_recorded": "Atlas Registrars Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://atlasregistrars.com/our-contact",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://atlasregistrars.com/our-contact/",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/47086_HONEYWELL_FLOUR_MILL_PLC-_QUARTER_5_-_FINANCIAL_STATEMENT_FOR_2026_FINANCIAL_STATEMENTS_MAY_2026.pdf",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292005013E6R7YD4G92"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: SEC register spells the email domain 'atlasregsistars.com', which does not resolve; use the website address. Netcup: SEC email domain is misspelt."
  },
  {
   "slug": "unity",
   "display_name": "Unity",
   "legal_name": "Unity Registrars Ltd",
   "trading_name": "Unity Registrars",
   "names_in_mapping_file": [
    "Unity Registrars Ltd"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://unityregistrarsng.com",
    "safe_to_link": false,
    "problem": "HTTP 503 (maintenance page) on 2026-11-26"
   },
   "primary_email": "info@unityregistrarsng.com",
   "primary_phone": "+2348033006038",
   "emails": [
    {
     "address": "info@unityregistrarsng.com",
     "label": "general",
     "sources": [
      "SEC register",
      "ICMR directory"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2348033006038",
     "range_end": null,
     "as_printed": "08033006038",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "25 Ogunlana Drive, Surulere, Lagos",
    "city": "Surulere",
    "state": "Lagos",
    "confidence": "Medium",
    "flag": "STALE"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "25 Ogunlana Drive, Surulere, Lagos",
     "city_state": "Lagos",
     "phone": "+234 803 300 6038",
     "email": "info@unityregistrarsng.com",
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?page=2&query=registrars",
     "show_on_page": true,
     "note": "HQ flag STALE."
    }
   ],
   "portals": [],
   "parent_group": null,
   "latest_operating_evidence": "NOT FOUND within 12 months. Newest: Veritas Kapital AGM notice Aug 2024; Stage 1 Unity Bank AGM notice Feb 2025; own site post dated 15 Oct 2025 (search index only)",
   "client_count": 2,
   "clients": [
    {
     "company": "Unity Bank Plc",
     "ticker": "UNITYBNK",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "STALE",
     "last_evidence_date": "2025-08-29",
     "registrar_as_recorded": "Unity Registrars Ltd"
    },
    {
     "company": "Veritas Kapital Assurance Plc",
     "ticker": "VERITASKAP",
     "security_type": "Equity",
     "sector": "FINANCIAL SERVICES",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "STALE",
     "last_evidence_date": "2024-08-26",
     "registrar_as_recorded": "Unity Registrars Ltd"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=2",
    "https://icmr.org.ng/unity-registrars-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?page=2&query=registrars",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/42061_VERITAS_KAPITAL_ASSURANCE_PLC-NOTICE_OF_ANNUAL_GENERAL_MEETING_CORPORATE_ACTIONS_AUGUST_2024.pdf",
    "https://icmr.org.ng/unity-registrars-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Website shows a maintenance page (HTTP 503). Second address source is the undated ICMR directory. No notice within 12 months naming Unity was found; newest client evidence is from 2025. Netcup: Needs human follow-up: confirm the firm still operates (call the SEC-listed number) and whether the website outage is temporary."
  },
  {
   "slug": "lancelot",
   "display_name": "Lancelot",
   "legal_name": "Lancelot Registrars And Investors Relations Limited",
   "trading_name": "Lancelot Registrars",
   "names_in_mapping_file": [
    "Lancelot Registrars And Investors Relations Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://lancelotregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@lancelotregistrars.com",
   "primary_phone": "+2349169660770",
   "emails": [
    {
     "address": "info@lancelotregistrars.com",
     "label": "general",
     "sources": [
      "registrar or group website",
      "client company filing"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2349169660770",
     "range_end": null,
     "as_printed": "+234 916 9660 770",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "245 Herbert Macaulay Way, Alagomeji, Yaba, Lagos",
    "city": "Yaba",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "245 Herbert Macaulay Way, Alagomeji, Yaba, Lagos",
     "city_state": "Lagos",
     "phone": "+234 916 966 0770",
     "email": "info@lancelotregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://lancelotregistrars.com/contact-us/",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [],
   "parent_group": "Lancelot Group (own team page names a Group Managing Director of Lancelot Group)",
   "latest_operating_evidence": "2026-04-27: Industrial & Medical Gases AGM notice on NGX names Lancelot (https://doclib.ngxgroup.com/Financial_NewsDocs/IMG_-_NOTICE_OF_ANNUAL_GENERAL_MEETING_2026.pdf)",
   "client_count": 1,
   "clients": [
    {
     "company": "Industrial & Medical Gases Nigeria Plc",
     "ticker": "IMG",
     "security_type": "Equity",
     "sector": "NATURAL RESOURCES",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-04-27",
     "registrar_as_recorded": "Lancelot Registrars And Investors Relations Limited"
    }
   ],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://lancelotregistrars.com/contact-us",
    "https://icmr.org.ng/lancelot-registrars-and-investor-relation-limited",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://lancelotregistrars.com/contact-us/",
    "https://doclib.ngxgroup.com/Financial_NewsDocs/IMG_-_NOTICE_OF_ANNUAL_GENERAL_MEETING_2026.pdf",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292006113F1S6C0D504",
    "https://icmr.org.ng/lancelot-registrars-and-investor-relation-limited/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: SEC register email is an individual's address and is withheld."
  },
  {
   "slug": "fsl",
   "display_name": "FSL",
   "legal_name": "FSL Registrars Limited",
   "trading_name": "FSL Registrars",
   "names_in_mapping_file": [],
   "priority": "lower (no mapped clients)",
   "website": {
    "url": "https://fsl.ng",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@fsl.ng",
   "primary_phone": "+2348151590112",
   "emails": [
    {
     "address": "info@fsl.ng",
     "label": "group general",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "tellme@fsl.ng",
     "label": "group",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2348151590112",
     "range_end": null,
     "as_printed": "+234 (815) 159-0112",
     "label": "all offices",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "Plot 688 Ahmodu Tijani Close, off Sanusi Fafunwa Street, Victoria Island, Lagos",
    "city": "Victoria Island",
    "state": "Lagos",
    "confidence": "Medium",
    "flag": "CONFLICT"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "group (registrar per SEC)",
     "address": "Plot 688 Ahmodu Tijani Close, off Sanusi Fafunwa Street, Victoria Island, Lagos",
     "city_state": "Lagos",
     "phone": "+234 815 159 0112",
     "email": "info@fsl.ng",
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "https://www.fsl.ng/contact-us",
     "show_on_page": true,
     "note": "CSCS LEI record of FSL Registrars (6 Mar 2026) gives Plot 866; SEC register and group site give Plot 688. Value re-read in the merge. HQ flag CONFLICT."
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (FSL)",
     "address": "Plot 363 Nanka Close, Zone 3, Abuja",
     "city_state": "Abuja, FCT",
     "phone": "+2348151590112",
     "email": "info@fsl.ng",
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://www.fsl.ng/contact-us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (FSL)",
     "address": "Stock Exchange Complex, No. 4 Ridge Road, GRA, Onitsha, Anambra State",
     "city_state": "Onitsha, Anambra",
     "phone": "+2348151590112",
     "email": "info@fsl.ng",
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://www.fsl.ng/contact-us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (FSL)",
     "address": "8 Ogui Road, Enugu, Enugu State",
     "city_state": "Enugu, Enugu",
     "phone": "+2348151590112",
     "email": "info@fsl.ng",
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://www.fsl.ng/contact-us",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (FSL)",
     "address": "2 Trans Amadi Industrial Layout, Port Harcourt, Rivers State",
     "city_state": "Port Harcourt, Rivers",
     "phone": "+2348151590112",
     "email": "info@fsl.ng",
     "confidence": "Low",
     "date": "2026-11-26",
     "source": "https://www.fsl.ng/contact-us",
     "show_on_page": true,
     "note": "Netcup run read this address as incomplete; the workstation read the full lines on the same page."
    }
   ],
   "portals": [],
   "parent_group": "FSL Capital group; website and offices are the group's",
   "latest_operating_evidence": "No client notice (no mapped clients). Live signals: SEC register lists it as Registrar (fidelity bond 'N/A'); LEI ACTIVE, updated 6 Mar 2026",
   "client_count": 0,
   "clients": [],
   "evidence_sources": [
    "https://sec.gov.ng/for-investors/find-a-registered-operator/?query=registrar&page=1",
    "https://fsl.ng/contact-us",
    "https://www.sec.gov.ng/for-investors/find-a-registered-operator/?query=registrars",
    "https://www.fsl.ng/contact-us",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292006752E3Q7D0C423",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292003768D9N8AI3J94"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "CSCS LEI record of FSL Registrars (6 Mar 2026) gives Plot 866; SEC register and group site give Plot 688. Value re-read in the merge. Workstation: SEC registration dated 6 January 2026. SEC register email is an individual's address and is withheld. No registrar-specific contact found. Netcup: SEC shows fidelity bond 'N/A'."
  },
  {
   "slug": "paxhil-minerva",
   "display_name": "Paxhil Minerva",
   "legal_name": "PAXHIL MINERVA REGISTRARS LIMITED",
   "trading_name": "Paxhill Minerva Registrars",
   "names_in_mapping_file": [],
   "priority": "lower (no mapped clients)",
   "website": {
    "url": "https://paxhillminervaregistrars.com",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "info@paxhillminervaregistrars.com",
   "primary_phone": "+2349078072602",
   "emails": [
    {
     "address": "info@paxhillminervaregistrars.com",
     "label": "general",
     "sources": [
      "registrar or group website"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2349078072602",
     "range_end": null,
     "as_printed": "+234 (0) 907 807 2602",
     "label": "main line",
     "type": "voice",
     "sources": [
      "registrar or group website"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "10 Bankole Oki Road, Ikoyi, Lagos",
    "city": "Ikoyi",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "10 Bankole Oki Road, Ikoyi, Lagos",
     "city_state": "Lagos",
     "phone": "+234 907 807 2602",
     "email": "info@paxhillminervaregistrars.com",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "https://paxhillminervaregistrars.com/contact/",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [],
   "parent_group": "Related company: Paxhill Minerva Trustees (per search result; not opened)",
   "latest_operating_evidence": "No client notice (no mapped clients). Live signals: own site says SEC licence as Registrar from 1 Jul 2024; LEI ACTIVE, updated 18 Dec 2025",
   "client_count": 0,
   "clients": [],
   "evidence_sources": [
    "https://paxhillminervaregistrars.com",
    "https://icmr.org.ng/lighthouse-registrars-limited-copy",
    "https://paxhillminervaregistrars.com/contact/",
    "https://leinew.cscs.ng/cscslei/lei-entity-details.php?lei=0292006058J6O9Z9I924",
    "https://icmr.org.ng/lighthouse-registrars-limited-copy/"
   ],
   "last_verified": "2026-11-26; Netcup-cited values re-checked 2026-11-27",
   "internal_research_notes": "Workstation: Name mismatch: SEC register spells 'Paxhil', website and ICMR spell 'Paxhill'. SEC register shows no address, phone or email. Netcup: Name spelling differs: SEC 'Paxhil', own site 'Paxhill'."
  }
 ],
 "without_contact_record": [
  {
   "registrar_as_recorded": "Centurion Registrars Limited (suspended; not on SEC register)",
   "reason": "Reported suspended by the SEC (March 2025); not found among SEC-registered registrars on 2026-11-26.",
   "clients": [
    {
     "company": "Vital Products Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Consumer Goods",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "Centurion Registrars Limited (suspended; not on SEC register)"
    },
    {
     "company": "Union Dicon Salt Plc",
     "ticker": "UNIONDICON",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "UNVERIFIED",
     "last_evidence_date": "2026-03-31",
     "registrar_as_recorded": "Centurion Registrars Limited (suspended; not on SEC register)"
    }
   ]
  },
  {
   "registrar_as_recorded": "ECO Securities (not on SEC register)",
   "reason": "Not on the SEC register as a registrar.",
   "clients": [
    {
     "company": "Resourcery PLC",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Technology",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "ECO Securities (not on SEC register)"
    }
   ]
  },
  {
   "registrar_as_recorded": "LENNAP Securities (not on SEC register)",
   "reason": "Not on the SEC register as a registrar.",
   "clients": [
    {
     "company": "International Packing Industries Nigeria Plc",
     "ticker": null,
     "security_type": "NASD",
     "sector": "Industrials",
     "board": "NASD OTC",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-11-25 (page retrieved; undated)",
     "registrar_as_recorded": "LENNAP Securities (not on SEC register)"
    }
   ]
  },
  {
   "registrar_as_recorded": "UNVERIFIED - not found",
   "reason": "Registrar not identified.",
   "clients": [
    {
     "company": "Ekocorp Plc",
     "ticker": "EKOCORP",
     "security_type": "Equity",
     "sector": "HEALTHCARE",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "UNVERIFIED",
     "last_evidence_date": null,
     "registrar_as_recorded": "UNVERIFIED - not found"
    }
   ]
  }
 ]
}
```
