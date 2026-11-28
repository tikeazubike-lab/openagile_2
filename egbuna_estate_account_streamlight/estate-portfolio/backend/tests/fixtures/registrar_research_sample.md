# Registrar research sample (hand-made fixture)

A small hand-made sample in the same format as
`docs/registrars/registrars_contact_details_final.md`: a short prose preamble
followed by exactly one JSON block holding the data. It is a fixture for the
unit tests of F-026c — none of the values are real research.

Rules mirrored from the real file (see spec F-026c, section 4):
- `show_on_page` gates emails and offices, `safe_to_link` gates websites and
  portals, `warning` rides along on phone labels.
- `head_office.confidence` is High or Medium; `head_office.flag` is OK,
  CONFLICT or STALE.
- `mapping_confidence` is High, Medium or Low; `mapping_flag` is OK,
  SINGLE-SOURCE, STALE or UNVERIFIED.
- `internal_research_notes`, `evidence_sources` and
  `latest_operating_evidence` are background, never page copy.

```json
{
 "generated": "2026-11-27",
 "country": "Nigeria",
 "registrar_count": 2,
 "mapping_rows": 5,
 "registrars": [
  {
   "slug": "alpha",
   "display_name": "Alpha",
   "legal_name": "Alpha Registrars Nigeria Limited",
   "trading_name": "Alpha Registrars Limited",
   "names_in_mapping_file": [
    "Alpha Registrars Nigeria Limited"
   ],
   "priority": "in scope",
   "website": {
    "url": "https://alpha.example",
    "safe_to_link": false,
    "problem": "TLS certificate does not match the domain"
   },
   "primary_email": "desk@alpha.example",
   "primary_phone": "+2341000000001",
   "emails": [
    {
     "address": "desk@alpha.example",
     "label": null,
     "sources": [
      "SEC register"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    },
    {
     "address": "backoffice@alpha.example",
     "label": "back office",
     "sources": [
      "registrar web page"
     ],
     "show_on_page": false,
     "reason_if_hidden": "staff directory, not confirmed"
    }
   ],
   "phones": [
    {
     "e164": "+2341000000001",
     "range_end": null,
     "as_printed": "01 000 0001",
     "label": "main line",
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    },
    {
     "e164": "+2348012345678",
     "range_end": null,
     "as_printed": "0801 234 5678",
     "label": "switchboard",
     "type": "voice",
     "sources": [
      "client company filing"
     ],
     "warning": null
    },
    {
     "e164": "+2341000000002",
     "range_end": null,
     "as_printed": "01 000 0002",
     "label": "after hours",
     "type": "voice",
     "sources": [
      "group website"
     ],
     "warning": "answered by the group desk, not by the registrar"
    }
   ],
   "head_office": {
    "address": "1 Alpha Way, Lagos",
    "city": "Lagos",
    "state": "Lagos",
    "confidence": "Medium",
    "flag": "CONFLICT"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "1 Alpha Way, Lagos",
     "city_state": "Lagos",
     "phone": "+2341000000001",
     "email": "desk@alpha.example",
     "confidence": "Medium",
     "date": "2026-11-26",
     "source": "registrar web page",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Group office",
     "is_head_office": false,
     "belongs_to": "group (Alpha Holdings)",
     "address": "2 Group Road, Lagos",
     "city_state": "Lagos",
     "phone": null,
     "email": null,
     "confidence": "High",
     "date": "2026-11-25",
     "source": "group website",
     "show_on_page": true,
     "note": null
    },
    {
     "type": "Branch",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "4 Hidden Street, Lagos",
     "city_state": "Lagos",
     "phone": null,
     "email": null,
     "confidence": "High",
     "date": "2026-11-25",
     "source": "registrar web page",
     "show_on_page": false,
     "note": null
    },
    {
     "type": "Liaison office",
     "is_head_office": false,
     "belongs_to": "registrar",
     "address": "3 Link Avenue, Abuja",
     "city_state": "Abuja",
     "phone": null,
     "email": null,
     "confidence": "High",
     "date": "2026-11-25",
     "source": "registrar web page",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [
    {
     "url": "https://portal.alpha.example",
     "description": null,
     "status": "address resolves",
     "safe_to_link": false
    },
    {
     "url": "https://etransfer.alpha.example",
     "description": "e-transfer portal",
     "status": "address resolves",
     "safe_to_link": true
    }
   ],
   "parent_group": "Alpha Holdings",
   "latest_operating_evidence": "background only, never page copy",
   "client_count": 5,
   "clients": [
    {
     "company": "Alpha Foods Plc",
     "ticker": "ALPHA",
     "security_type": "Equity",
     "sector": "CONSUMER GOODS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-10-30",
     "registrar_as_recorded": "Alpha Registrars Nigeria Limited"
    },
    {
     "company": "Weak Co Plc",
     "ticker": "WEAKCO",
     "security_type": "Equity",
     "sector": "BANKS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "SINGLE-SOURCE",
     "last_evidence_date": "2026-01-01",
     "registrar_as_recorded": "Alpha Registrars Nigeria Limited"
    },
    {
     "company": "Unverified Co Plc",
     "ticker": "UNVCO",
     "security_type": "Equity",
     "sector": "BANKS",
     "board": "Main Board",
     "mapping_confidence": "Medium",
     "mapping_flag": "UNVERIFIED",
     "last_evidence_date": "2026-11-25",
     "registrar_as_recorded": "Alpha Registrars Nigeria Limited"
    },
    {
     "company": "Ghost Co Plc",
     "ticker": "GHOST",
     "security_type": "Equity",
     "sector": "BANKS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-11-25",
     "registrar_as_recorded": "Alpha Registrars Nigeria Limited"
    },
    {
     "company": "No Ticker Co Plc",
     "ticker": null,
     "security_type": "Equity",
     "sector": "BANKS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-11-25",
     "registrar_as_recorded": "Alpha Registrars Nigeria Limited"
    }
   ],
   "evidence_sources": [
    "https://example.invalid/sec-register"
   ],
   "last_verified": "2026-11-27",
   "internal_research_notes": "background only: never-a-page-value 999-777"
  },
  {
   "slug": "newbies",
   "display_name": "Newbies",
   "legal_name": "Newbies Registrars Limited",
   "trading_name": "Newbies Registrars Limited",
   "names_in_mapping_file": [
    "Newbies Registrars Limited"
   ],
   "priority": "new record",
   "website": {
    "url": "https://newbies.example",
    "safe_to_link": true,
    "problem": null
   },
   "primary_email": "hello@newbies.example",
   "primary_phone": "+2342000000001",
   "emails": [
    {
     "address": "hello@newbies.example",
     "label": null,
     "sources": [
      "SEC register"
     ],
     "show_on_page": true,
     "reason_if_hidden": null
    }
   ],
   "phones": [
    {
     "e164": "+2342000000001",
     "range_end": null,
     "as_printed": "02 000 0001",
     "label": null,
     "type": "voice",
     "sources": [
      "SEC register"
     ],
     "warning": null
    }
   ],
   "head_office": {
    "address": "5 Newbie Close, Ikeja, Lagos",
    "city": "Ikeja",
    "state": "Lagos",
    "confidence": "High",
    "flag": "OK"
   },
   "offices": [
    {
     "type": "Head office",
     "is_head_office": true,
     "belongs_to": "registrar",
     "address": "5 Newbie Close, Ikeja, Lagos",
     "city_state": "Ikeja, Lagos",
     "phone": "+2342000000001",
     "email": "hello@newbies.example",
     "confidence": "High",
     "date": "2026-11-26",
     "source": "registrar web page",
     "show_on_page": true,
     "note": null
    }
   ],
   "portals": [],
   "parent_group": null,
   "latest_operating_evidence": "background only, never page copy",
   "client_count": 1,
   "clients": [
    {
     "company": "Newbie Co Plc",
     "ticker": "NEWBIE",
     "security_type": "Equity",
     "sector": "BANKS",
     "board": "Main Board",
     "mapping_confidence": "High",
     "mapping_flag": "OK",
     "last_evidence_date": "2026-11-25",
     "registrar_as_recorded": "Newbies Registrars Limited"
    }
   ],
   "evidence_sources": [],
   "last_verified": "2026-11-27",
   "internal_research_notes": "background only"
  }
 ],
 "without_contact_record": [
  {
   "registrar_as_recorded": "Nowhere Registrars Limited",
   "reason": "not on the SEC register on 2026-11-26",
   "clients": [
    {
     "company": "No Record Co Plc",
     "ticker": "NOREC",
     "security_type": "Equity",
     "sector": "BANKS",
     "board": "Main Board",
     "mapping_confidence": "Low",
     "mapping_flag": "UNVERIFIED",
     "last_evidence_date": "2026-11-25",
     "registrar_as_recorded": "Nowhere Registrars Limited"
    }
   ]
  }
 ]
}
```
