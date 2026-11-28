# backend/scripts/import_registrar_research.py
"""
F-026c — registrar research import (contacts, duplicate merge, company links).

Spec: ``.context/feature-specs/F-026c-registrar-research-import.md`` (HO-160).
Data change only: no application code, schema or migration changes.

The module is split into three layers so that everything except the engine can
be tested against a real database inside a rollback:

1. **Pure layer** (no DB imports, no DB access at import time):
   ``parse_research`` (reads the single ```json block), ``classify``,
   the label / normalisation helpers and ``build_plan(research, snapshot,
   resolution_table) -> Plan``. The §3 resolution table is the module constant
   ``RESOLUTION_TABLE`` *and* an argument to ``build_plan``, so tests pass their
   own ids. A mismatch raises :class:`ResolutionError` before any plan is built.
2. **DB layer**: ``load_snapshot(session)``, ``apply_plan(session, plan) ->
   UndoRecord``, ``undo(session, record)``. They take an ``AsyncSession``,
   never commit and never create engines.
3. **CLI**: owns the engine and the transaction — ``SET TRANSACTION READ ONLY``
   as the first statement of the preview transaction, ``--confirm-db``
   (compared with ``select current_database()``), and the undo record that
   A-7 writes **before** the COMMIT (``--undo-out <path|->``, the ``-`` form
   printing it on stdout between the ``F026C UNDO JSON`` markers).

Usage::

    # preview (default): read-only transaction, prints the plan + counts
    python scripts/import_registrar_research.py
    python scripts/import_registrar_research.py --research PATH

    # apply: one transaction, all or nothing; the undo record is written
    # BEFORE the commit, and a failing writer rolls the apply back (AC-17)
    python scripts/import_registrar_research.py --apply --confirm-db epm_test \
        --undo-out docs/registrars/import-runs/run1.json

    # apply in the container: only stdout reaches the host
    python scripts/import_registrar_research.py --apply --confirm-db epm_test \
        --undo-out -

    # undo a previous apply, one transaction
    python scripts/import_registrar_research.py \
        --undo docs/registrars/import-runs/<UTC>-<db>.json --confirm-db epm_test

``cli(argv, research_text=...)`` parses ``research_text`` instead of reading
``--research``; that is how the preview is run inside the production container,
where only stdin is available (the module must import cleanly when piped to
``python -`` with cwd ``/app``: ``__file__`` is only touched through
``globals().get("__file__")`` and only when it exists).

Entry point (skipped when the module is embedded by a wrapper)::

    if __name__ == "__main__" and not globals().get("_F026C_EMBEDDED"):
        sys.exit(asyncio.run(cli(sys.argv[1:])))

The script refuses to run without ``DATABASE_URL`` and never prints the URL or
its password.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import func, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

__all__ = [
    # errors
    "ResearchImportError", "ParseError", "ResolutionError", "ConfirmDatabaseError",
    # pure layer
    "Research", "Snapshot", "RegistrarRow", "FieldRow", "LinkRow", "CompanyRow",
    "RequirementRow", "ResolutionEntry", "RESOLUTION_TABLE", "Plan", "UndoRecord",
    "parse_research", "classify", "normalise", "phone_label", "email_label",
    "website_field", "portal_field", "office_label", "build_plan", "format_plan",
    "apply_ops_to_snapshot", "check_confirm_db",
    # ops (needed by tests and by apply_plan)
    "CreateRegistrarOp", "RenameRegistrarOp", "UpdateRegistrarOp",
    "SoftDeleteRegistrarOp", "MoveFieldOp", "CreateFieldOp", "SoftDeleteLinkOp",
    "EnsurePrimaryLinkOp", "CreateLinkOp", "RepointLinkOp", "RepointRequirementOp",
    "UpdateCompanyOp",
    # DB layer
    "load_snapshot", "apply_plan", "undo",
    # CLI
    "cli", "amain",
]


# ─── errors ────────────────────────────────────────────────────────────────────

class ResearchImportError(Exception):
    """Base class for every error this script raises on purpose."""


class ParseError(ResearchImportError):
    """The research file does not contain exactly one valid JSON block."""


class ResolutionError(ResearchImportError):
    """The §3 resolution table does not match the file or the snapshot."""


class ConfirmDatabaseError(ResearchImportError):
    """--confirm-db is missing or does not match the connected database."""


# ─── snapshot rows (plain dataclasses: no DB access) ───────────────────────────

@dataclass
class RegistrarRow:
    id: int
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None
    response_rating: int | None = None
    notes: str | None = None
    status: str | None = None
    jurisdiction: str = "nigeria"
    deleted_at: Any = None


@dataclass
class FieldRow:
    id: int
    registrar_id: int
    field_type: str
    field_value: str
    label: str | None = None
    sort_order: int = 0
    deleted_at: Any = None


@dataclass
class LinkRow:
    id: int
    company_id: int
    registrar_id: int
    role: str = "primary"
    deleted_at: Any = None


@dataclass
class CompanyRow:
    id: int
    ticker: str | None = None
    name: str | None = None
    registrar_id: int | None = None
    deleted_at: Any = None


@dataclass
class RequirementRow:
    id: int
    registrar_id: int
    deleted_at: Any = None


@dataclass
class Snapshot:
    """The current rows the plan is built from (spec F-026c §4)."""
    registrars: dict = field(default_factory=dict)
    fields: list = field(default_factory=list)
    links: list = field(default_factory=list)
    companies: list = field(default_factory=list)
    requirements: list = field(default_factory=list)


@dataclass(frozen=True)
class ResolutionEntry:
    """One row of the §3 resolution table. ``canonical is None`` = new record."""
    slug: str
    canonical: int | None
    duplicates: tuple = ()
    final_name: str | None = None


@dataclass
class Research:
    """The parsed research file (one JSON block)."""
    registrars: list = field(default_factory=list)
    without_contact_record: list = field(default_factory=list)
    source: str | None = field(default=None, compare=False)


# ─── plan operations ────────────────────────────────────────────────────────────

@dataclass
class CreateRegistrarOp:
    key: tuple                       # ("new", slug) — id unknown until apply
    name: str
    source_slug: str = ""
    jurisdiction: str = "nigeria"
    status: str = "active"


@dataclass
class RenameRegistrarOp:
    registrar_id: int
    new_name: str


@dataclass
class UpdateRegistrarOp:
    registrar_key: Any                # int id or ("new", slug)
    changes: dict


@dataclass
class SoftDeleteRegistrarOp:
    registrar_id: int


@dataclass
class MoveFieldOp:
    field_id: int
    to_registrar_id: Any


@dataclass
class CreateFieldOp:
    registrar_key: Any
    field_type: str
    field_value: str
    label: str | None
    sort_order: int


@dataclass
class SoftDeleteLinkOp:
    link_id: int


@dataclass
class EnsurePrimaryLinkOp:
    company_id: int
    registrar_key: Any
    link_id: int | None = None       # the soft-deleted row to reactivate
    role: str = "primary"            # A-1/A-2: role set together with deleted_at=NULL


@dataclass
class CreateLinkOp:
    company_id: int
    registrar_key: Any
    role: str = "primary"


@dataclass
class RepointLinkOp:
    link_id: int
    to_registrar_id: Any


@dataclass
class RepointRequirementOp:
    requirement_id: int
    to_registrar_id: Any


@dataclass
class UpdateCompanyOp:
    company_id: int
    changes: dict


COUNT_KEYS = (
    "registrars_created", "registrars_merged", "registrars_soft_deleted",
    "registrars_renamed", "fields_added", "fields_moved",
    "legacy_columns_filled", "links_created", "links_reactivated",
    "links_soft_deleted", "links_repointed", "requirements_repointed",
    "companies_registrar_changed",
)

LEGACY_COLUMNS = ("email", "phone", "address", "website")


@dataclass
class Plan:
    ops: list = field(default_factory=list)
    lines: list = field(default_factory=list)          # what the apply will do
    report_lines: list = field(default_factory=list)   # informational only
    counts: dict = field(default_factory=lambda: {key: 0 for key in COUNT_KEYS})
    report_counts: dict = field(default_factory=lambda: {
        "held_back": 0, "unmatched": 0, "without_contact_record": 0,
    })
    held_back: list = field(default_factory=list)
    unmatched: list = field(default_factory=list)
    without_contact_record: list = field(default_factory=list)

    def add(self, op, line: str) -> None:
        self.ops.append(op)
        self.lines.append(line)

    @property
    def empty(self) -> bool:
        return not self.ops

    def counts_block(self) -> list:
        c, r = self.counts, self.report_counts
        return [
            (f"registrars: created={c['registrars_created']} merged={c['registrars_merged']} "
             f"soft-deleted={c['registrars_soft_deleted']} renamed={c['registrars_renamed']}"),
            f"contact fields: added={c['fields_added']} moved={c['fields_moved']}",
            f"legacy columns filled={c['legacy_columns_filled']}",
            (f"links: created={c['links_created']} reactivated={c['links_reactivated']} "
             f"soft-deleted={c['links_soft_deleted']} repointed={c['links_repointed']}"),
            f"requirements repointed={c['requirements_repointed']}",
            f"companies.registrar_id changed={c['companies_registrar_changed']}",
            f"held back (weak)={r['held_back']}",
            f"unmatched={r['unmatched']}",
            f"without contact record={r['without_contact_record']}",
        ]


@dataclass
class UndoRecord:
    """Every row a --apply touched, with the previous values it had."""
    database: str = ""
    applied_at: str = ""
    counts: dict = field(default_factory=dict)
    entries: list = field(default_factory=list)

    def add_insert(self, table: str, row_id: int) -> None:
        self.entries.append({"table": table, "id": row_id, "inserted": True})

    def add_update(self, table: str, row_id: int, previous: dict) -> None:
        self.entries.append({
            "table": table, "id": row_id,
            "previous": {k: _encode(v) for k, v in previous.items()},
        })

    @property
    def inserted_rows(self) -> list:
        """[(table, id), ...] of every row the apply inserted."""
        return [(e["table"], e["id"]) for e in self.entries if e.get("inserted")]

    def to_json(self) -> dict:
        return {
            "database": self.database,
            "applied_at": self.applied_at,
            "counts": self.counts,
            "entries": self.entries,
        }

    @classmethod
    def from_json(cls, data: dict) -> "UndoRecord":
        return cls(
            database=data.get("database", ""),
            applied_at=data.get("applied_at", ""),
            counts=data.get("counts", {}),
            entries=list(data.get("entries", [])),
        )


def _encode(value):
    """JSON-safe encoding that survives the round trip back to SQL types."""
    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, Decimal):
        return {"__type__": "decimal", "value": str(value)}
    return value


def _decode(value):
    if isinstance(value, dict) and value.get("__type__") == "datetime":
        return datetime.fromisoformat(value["value"])
    if isinstance(value, dict) and value.get("__type__") == "decimal":
        return Decimal(value["value"])
    return value


# ─── working copy (spec §9 A-6: plan integrity) ────────────────────────────────

def _planned_deleted_at():
    """The working copy's stand-in for the ``deleted_at = now()`` an apply
    would write. Only truthiness matters; the idiom matches the tests' own
    soft-deleted fixture rows."""
    return datetime.now(timezone.utc)


class _WorkCopy:
    """A copy of the snapshot that every planned op updates while it is being
    planned (spec §9 A-6):

    * **no row/column is changed by two ops** — every later read sees the
      state the plan has produced up to that point, so an op can never repeat
      an earlier one (audits #1 and #9);
    * every "before" value printed in a plan line is the value the row holds
      at that point of the plan;
    * rows the apply *creates* get a synthetic id (max(existing)+1, never a
      real id): planning never writes, so the id only has to be unique and
      stable inside this copy. ``apply_plan`` uses the database's ids.

    :func:`apply_ops_to_snapshot` below runs the same ``apply`` over a whole
    plan, which is how the tests read the post-apply state.
    """

    def __init__(self, snapshot: Snapshot):
        self.snap = Snapshot(
            registrars={row_id: replace(row)
                        for row_id, row in snapshot.registrars.items()},
            fields=[replace(row) for row in snapshot.fields],
            links=[replace(row) for row in snapshot.links],
            companies=[replace(row) for row in snapshot.companies],
            requirements=[replace(row) for row in snapshot.requirements],
        )
        self.created: dict = {}             # ("new", slug) -> synthetic id
        existing_ids = (
            [row.id for row in self.snap.registrars.values()]
            + [row.id for row in self.snap.fields]
            + [row.id for row in self.snap.links]
            + [row.id for row in self.snap.companies]
            + [row.id for row in self.snap.requirements]
        )
        self._next_id = max(existing_ids, default=0) + 1

    def _new_id(self) -> int:
        row_id = self._next_id
        self._next_id += 1
        return row_id

    def resolved(self, key):
        """The snapshot id of a target: an int id as it is, or the synthetic
        id a ("new", slug) row got in this copy (the key itself while the row
        does not exist yet)."""
        return key if isinstance(key, int) else self.created.get(key, key)

    def _value(self, value):
        """A change value: a scalar, or a ("new", slug) key to resolve."""
        return self.resolved(value) if isinstance(value, tuple) else value

    @staticmethod
    def _find(rows, row_id):
        for row in rows:
            if row.id == row_id:
                return row
        raise ResearchImportError(
            f"the plan touches row #{row_id} which is not in the snapshot")

    def _find_registrar(self, row_id) -> RegistrarRow:
        return self._find(list(self.snap.registrars.values()), row_id)

    def apply(self, op) -> None:
        """Apply one planned op to the working copy, mirroring exactly what
        ``apply_plan`` will do to the row (same columns, same rules)."""
        if isinstance(op, CreateRegistrarOp):
            row_id = self._new_id()
            self.created[op.key] = row_id
            self.snap.registrars[row_id] = RegistrarRow(
                id=row_id, name=op.name, status=op.status,
                jurisdiction=op.jurisdiction, deleted_at=None,
            )
        elif isinstance(op, RenameRegistrarOp):
            self._find_registrar(op.registrar_id).name = op.new_name
        elif isinstance(op, UpdateRegistrarOp):
            row = self._find_registrar(self.resolved(op.registrar_key))
            for column, value in op.changes.items():
                setattr(row, column, self._value(value))
        elif isinstance(op, SoftDeleteRegistrarOp):
            self._find_registrar(op.registrar_id).deleted_at = \
                _planned_deleted_at()
        elif isinstance(op, MoveFieldOp):
            self._find(self.snap.fields, op.field_id).registrar_id = \
                self.resolved(op.to_registrar_id)
        elif isinstance(op, CreateFieldOp):
            self.snap.fields.append(FieldRow(
                id=self._new_id(), registrar_id=self.resolved(op.registrar_key),
                field_type=op.field_type, field_value=op.field_value,
                label=op.label, sort_order=op.sort_order, deleted_at=None,
            ))
        elif isinstance(op, SoftDeleteLinkOp):
            self._find(self.snap.links, op.link_id).deleted_at = \
                _planned_deleted_at()
        elif isinstance(op, EnsurePrimaryLinkOp):
            if op.link_id is not None:
                row = self._find(self.snap.links, op.link_id)
                row.deleted_at = None
                row.role = op.role
            else:
                # the same rule apply_plan() uses at run time: reactivate the
                # soft-deleted (company, registrar) row when there is one,
                # insert one otherwise (F4: never a second row for a pair)
                row = next((link for link in self.snap.links
                            if link.company_id == op.company_id
                            and link.registrar_id == self.resolved(op.registrar_key)
                            and link.deleted_at), None)
                if row is None:
                    row = LinkRow(id=self._new_id(), company_id=op.company_id,
                                  registrar_id=self.resolved(op.registrar_key),
                                  role=op.role, deleted_at=None)
                    self.snap.links.append(row)
                else:
                    row.deleted_at = None
                    row.role = op.role
        elif isinstance(op, CreateLinkOp):
            self.snap.links.append(LinkRow(
                id=self._new_id(), company_id=op.company_id,
                registrar_id=self.resolved(op.registrar_key),
                role=op.role, deleted_at=None,
            ))
        elif isinstance(op, RepointLinkOp):
            self._find(self.snap.links, op.link_id).registrar_id = \
                self.resolved(op.to_registrar_id)
        elif isinstance(op, RepointRequirementOp):
            self._find(self.snap.requirements, op.requirement_id).registrar_id = \
                self.resolved(op.to_registrar_id)
        elif isinstance(op, UpdateCompanyOp):
            row = self._find(self.snap.companies, op.company_id)
            for column, value in op.changes.items():
                setattr(row, column, self._value(value))
        else:                                            # pragma: no cover
            raise ResearchImportError(
                f"working copy: unknown operation {op!r}")


def apply_ops_to_snapshot(snapshot: Snapshot, ops: list) -> Snapshot:
    """What ``snapshot`` looks like once every planned op has run: a fresh
    working copy driven through the plan (spec §9 A-6 / A-3 idempotency)."""
    work = _WorkCopy(snapshot)
    for op in ops:
        work.apply(op)
    return work.snap


# ─── pure layer: parsing, labels, normalisation ────────────────────────────────

_JSON_BLOCK = re.compile(r"```json[ \t]*\r?\n(.*?)\r?\n```", re.DOTALL)


def _default_research_path() -> Path:
    """docs/registrars/registrars_contact_details_final.md relative to the EPM
    dir — or relative to the cwd when the module is piped to ``python -``."""
    filename = globals().get("__file__")
    if filename:
        path = Path(filename)
        if path.exists():                      # never trust __file__ blindly
            return path.resolve().parents[2] / "docs" / "registrars" / \
                "registrars_contact_details_final.md"
    return Path("docs") / "registrars" / "registrars_contact_details_final.md"


def parse_research(source=None, *, text: str | None = None) -> Research:
    """Parse the research markdown: prose + exactly one fenced ```json block.

    ``text`` (the container's stdin path) wins over ``source``; with neither,
    the default file is read.
    """
    if text is not None:
        raw, origin = text, "<research_text>"
    elif source is not None:
        origin = str(source)
        try:
            raw = Path(source).read_text(encoding="utf-8")
        except OSError as exc:
            raise ParseError(f"{origin}: cannot read the research file: {exc}") from exc
    else:
        origin = str(_default_research_path())
        raw = _default_research_path().read_text(encoding="utf-8")

    blocks = _JSON_BLOCK.findall(raw)
    if len(blocks) != 1:
        raise ParseError(
            f"{origin}: expected exactly one ```json block, found {len(blocks)}"
        )
    try:
        data = json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        raise ParseError(f"{origin}: the json block does not parse: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("registrars"), list):
        raise ParseError(f"{origin}: the json block has no 'registrars' list")
    return Research(
        registrars=data["registrars"],
        without_contact_record=list(data.get("without_contact_record") or []),
        source=origin,
    )


def normalise(value, kind: str | None = None) -> str:
    """Spec §4.1.4: case-folded, whitespace-collapsed; digits-only for phones.

    A-5 (audit #8): for websites and portals one trailing ``/`` is stripped
    before the values are compared, so ``https://x.example/`` and
    ``https://x.example`` are the same value. Any value that *looks* like a
    URL counts too: an unsafe website or portal is stored with the type
    ``other`` (§4.2) and still has to compare equal.
    """
    if value is None:
        return ""
    text_value = str(value)
    if kind == "phone":
        return re.sub(r"\D", "", text_value)
    text_value = " ".join(text_value.split()).casefold()
    if kind in ("website", "portal") or text_value.startswith(("http://", "https://")):
        if text_value.endswith("/") and not text_value.endswith("://"):
            text_value = text_value[:-1]
    return text_value


def classify(client: dict) -> str:
    """Spec §4.4: firm unless the mapping is Low or UNVERIFIED."""
    if client.get("mapping_confidence") == "Low":
        return "weak"
    if client.get("mapping_flag") == "UNVERIFIED":
        return "weak"
    return "firm"


def _clip(value: str, limit: int = 100) -> str:
    return value if len(value) <= limit else value[:limit]


def phone_label(entry: dict) -> str:
    """Spec §4.2: the file label (or "Phone") + ' — ' + warning, max 100 chars."""
    base = (entry.get("label") or "").strip() or "Phone"
    warning = entry.get("warning")
    label = f"{base} — {warning}" if warning else base
    return _clip(label)


def email_label(entry: dict) -> str:
    base = (entry.get("label") or "").strip() or "Email"
    return _clip(base)


def website_field(website: dict | None) -> tuple | None:
    """Spec §4.2: 'website' only when safe_to_link, else 'other' with the
    explanatory label. A null website adds nothing."""
    if not website or not website.get("url"):
        return None
    if website.get("safe_to_link"):
        return ("website", "Website")
    return ("other", "Website (not verified, copy manually)")


def portal_field(portal: dict | None) -> tuple | None:
    """Spec §4.2: portals follow the website rule, label = description."""
    if not portal or not portal.get("url"):
        return None
    label = _clip((portal.get("description") or "").strip() or "Online portal")
    field_type = "website" if portal.get("safe_to_link") else "other"
    return (field_type, label)


def office_label(office: dict, head_office: dict | None = None) -> str:
    """Spec §4.2/AC-7: ' (please confirm)' when the confidence is not High or
    when it is the head office and its flag is not OK. Max 100 chars."""
    head_office = head_office or {}
    base = (office.get("type") or "Office").strip() or "Office"
    needs_confirm = office.get("confidence") != "High"
    if office.get("is_head_office") and head_office.get("flag") != "OK":
        needs_confirm = True
    if not needs_confirm:
        return _clip(base)
    suffix = " (please confirm)"
    return _clip(base, 100 - len(suffix)) + suffix


def check_confirm_db(confirm_db, connected_db) -> None:
    """AC-14: --confirm-db must be given and must equal current_database()."""
    if not confirm_db:
        raise ConfirmDatabaseError("--confirm-db <dbname> is required")
    if confirm_db != connected_db:
        raise ConfirmDatabaseError(
            f"--confirm-db {confirm_db!r} does not match the connected "
            f"database {connected_db!r}"
        )


# ─── §3 resolution table (authoritative; the script never guesses) ─────────────

def _entry(slug, canonical, duplicates, final_name):
    return ResolutionEntry(
        slug=slug, canonical=canonical, duplicates=tuple(duplicates),
        final_name=final_name,
    )


RESOLUTION_TABLE: dict = {
    # slug: canonical id, duplicates merged into it, final name (None = keep)
    "meristem": _entry("meristem", 2, (9, 57), "Meristem Registrars"),
    "africa-prudential": _entry("africa-prudential", 50, (6,), None),
    "first-registrars": _entry("first-registrars", 52, (11,), None),
    "greenwich": _entry("greenwich", 8, (3, 56),
                        "Greenwich Registrars & Data Solutions Limited"),
    "coronation": _entry("coronation", 51, (12,), None),
    "cardinalstone": _entry("cardinalstone", 55, (21,), None),
    "veritas": _entry("veritas", 13, (53,), "Veritas Registrars Limited"),
    "unity": _entry("unity", 1, (17,), "Unity Registrars"),
    "atlas": _entry("atlas", 7, (), "Atlas Registrars Limited"),
    "datamax": _entry("datamax", 54, (), None),
    "pace": _entry("pace", 58, (), None),
    "crescent": _entry("crescent", 59, (), None),
    "carnation": _entry("carnation", 61, (), None),
    "apel": _entry("apel", None, (), "Apel Registrars And Corporate Services Limited"),
    "cordros": _entry("cordros", None, (), "Cordros Registrars Limited"),
    "lighthouse": _entry("lighthouse", None, (), "Lighthouse Registrars Ltd"),
    "pac": _entry("pac", None, (), "PAC Registrars & Investor Services Limited"),
    "lancelot": _entry("lancelot", None, (),
                       "Lancelot Registrars And Investors Relations Limited"),
    "fsl": _entry("fsl", None, (), "FSL Registrars Limited"),
    "paxhil-minerva": _entry("paxhil-minerva", None, (),
                             "Paxhil Minerva Registrars Limited"),
}


# ─── plan building (pure) ──────────────────────────────────────────────────────

def _fmt_key(key) -> str:
    return f"#{key}" if isinstance(key, int) else f"new[{key[1]}]"


class _Planner:
    def __init__(self, research: Research, snapshot: Snapshot, table: dict):
        self.research = research
        # A-6: every read below goes through the working copy, and _add()
        # feeds each planned op back into it before the next read.
        self.work = _WorkCopy(snapshot)
        self.snap = self.work.snap
        self.table = table
        self.plan = Plan()
        self.targets: dict = {}            # slug -> int id | ("new", slug)
        self.dup_legacy: dict = {}         # key -> [merged duplicates]
        self._merged = 0

    # ── verification (spec §3 / AC-14) ────────────────────────────────────
    def _verify_table(self) -> None:
        file_slugs = {entry["slug"] for entry in self.research.registrars}
        table_slugs = set(self.table)
        if file_slugs != table_slugs:
            raise ResolutionError(
                "resolution table does not match the file: "
                f"missing={sorted(file_slugs - table_slugs)} "
                f"unknown={sorted(table_slugs - file_slugs)}"
            )
        for slug, entry in self.table.items():
            if entry.slug != slug:
                raise ResolutionError(f"{slug}: resolution key and slug differ")
            word = slug.split("-")[0].casefold()
            if entry.canonical is None:
                if not entry.final_name:
                    raise ResolutionError(f"{slug}: a new registrar needs a final_name")
                if entry.duplicates:
                    raise ResolutionError(f"{slug}: a new registrar cannot have duplicates")
                continue
            canonical = self.snap.registrars.get(entry.canonical)
            if canonical is None:
                raise ResolutionError(
                    f"{slug}: canonical registrar #{entry.canonical} does not exist")
            if canonical.deleted_at:
                raise ResolutionError(
                    f"{slug}: canonical registrar #{entry.canonical} is soft-deleted")
            if word not in canonical.name.casefold():
                raise ResolutionError(
                    f"{slug}: registrar #{entry.canonical} name {canonical.name!r} "
                    f"does not contain {word!r}")
            for duplicate in entry.duplicates:
                row = self.snap.registrars.get(duplicate)
                if row is None:
                    raise ResolutionError(
                        f"{slug}: duplicate registrar #{duplicate} does not exist")
                if word not in row.name.casefold():
                    raise ResolutionError(
                        f"{slug}: duplicate #{duplicate} name {row.name!r} "
                        f"does not contain {word!r}")
                # A soft-deleted duplicate is already merged: skipped, not an
                # error — that is what makes a second --apply plan zero changes.

    def _resolve_targets(self) -> None:
        for slug, entry in self.table.items():
            if entry.canonical is not None:
                self.targets[slug] = entry.canonical
                continue
            existing = None
            for row in self.snap.registrars.values():
                if row.deleted_at is None and row.name == entry.final_name:
                    existing = row
                    break
            # already created by an earlier run => use its id (idempotent)
            self.targets[slug] = existing.id if existing else ("new", slug)

    # ── steps ─────────────────────────────────────────────────────────────
    def run(self) -> Plan:
        self._verify_table()
        self._resolve_targets()
        self._create_new_registrars()
        self._rename_canonicals()
        self._merge_duplicates()
        self._build_contacts()
        self._build_links()
        self._finish()
        return self.plan

    # ── the working copy (A-6) ────────────────────────────────────────────
    def _add(self, op, line: str) -> None:
        """Plan one operation AND record it on the working copy, so every
        later read sees the state at that point of the plan."""
        self.plan.add(op, line)
        self.work.apply(op)

    def _key_id(self, key):
        """The snapshot id of a target (int ids pass through)."""
        return self.work.resolved(key)

    def _links_at(self, key, *, active_only: bool = False) -> list:
        """All company_registrars rows pointing at a target right now."""
        resolved = self._key_id(key)
        return [link for link in self.snap.links
                if link.registrar_id == resolved
                and (not active_only or not link.deleted_at)]

    def _companies_at(self, key, *, active_only: bool = False) -> set:
        return {link.company_id
                for link in self._links_at(key, active_only=active_only)}

    def _row_for(self, company_id, key, *, soft_deleted: bool | None = None):
        """The (company, target) row, filtered by deleted_at when asked."""
        resolved = self._key_id(key)
        return next((link for link in self.snap.links
                     if link.company_id == company_id
                     and link.registrar_id == resolved
                     and (soft_deleted is None
                          or bool(link.deleted_at) == soft_deleted)), None)

    def _values_for(self, key) -> set:
        """Normalised values of every active field the target holds *now*
        (A-6: fields a previous op moved in are already there; A-5: the
        website/portal slash rule comes from normalise)."""
        resolved = self._key_id(key)
        return {normalise(row.field_value, row.field_type)
                for row in self.snap.fields
                if row.registrar_id == resolved and not row.deleted_at}

    def _create_new_registrars(self) -> None:
        for slug, entry in self.table.items():
            key = self.targets[slug]
            if not isinstance(key, tuple):
                continue
            self._add(
                CreateRegistrarOp(key=key, name=entry.final_name, source_slug=slug),
                f"create registrar {entry.final_name!r} (slug {slug})",
            )

    def _rename_canonicals(self) -> None:
        for slug, entry in self.table.items():
            if entry.canonical is None or not entry.final_name:
                continue
            row = self.snap.registrars[entry.canonical]
            if row.name == entry.final_name:
                continue
            self._add(
                RenameRegistrarOp(registrar_id=row.id, new_name=entry.final_name),
                f"registrar #{row.id}: rename {row.name!r} -> {entry.final_name!r}",
            )

    def _merge_duplicates(self) -> None:
        """Spec §4.1 — merge each duplicate D into its canonical K."""
        for slug, entry in self.table.items():
            if not entry.duplicates:
                continue
            key = entry.canonical
            # A-6: k_row is the working copy, so the rating/notes checks below
            # see what an earlier op in this plan has already written.
            k_row = self.snap.registrars[key]
            for duplicate in entry.duplicates:
                d_row = self.snap.registrars[duplicate]
                if d_row.deleted_at:
                    continue                       # already merged
                self._merge_one(key, duplicate, d_row)
                # rating/notes: copy the rating only when K has none, append
                # the notes with the [merged from #D] prefix
                changes = {}
                if k_row.response_rating is None and d_row.response_rating is not None:
                    changes["response_rating"] = d_row.response_rating
                if d_row.notes:
                    prefix = f"[merged from #{duplicate}] "
                    changes["notes"] = (f"{k_row.notes}\n" if k_row.notes else "") + prefix + d_row.notes
                if changes:
                    self._add(
                        UpdateRegistrarOp(registrar_key=key, changes=changes),
                        f"registrar {_fmt_key(key)}: merge values from "
                        f"#{duplicate} ({', '.join(sorted(changes))})",
                    )
                self._add(
                    SoftDeleteRegistrarOp(registrar_id=duplicate),
                    f"registrar #{duplicate}: soft-delete (merged into {_fmt_key(key)})",
                )
                self.dup_legacy.setdefault(key, []).append(d_row)
                self._merged += 1

    def _merge_one(self, key: int, duplicate: int, d_row: RegistrarRow) -> None:
        # 1. company_registrars rows: every lookup goes through the working
        #    copy, so a row an earlier op repointed or retired is already
        #    reflected here (A-6: never touch one row/column twice).
        for link in [row for row in self.snap.links
                     if row.registrar_id == duplicate and not row.deleted_at]:
            k_row = self._row_for(link.company_id, key)
            if k_row is None:
                self._add(
                    RepointLinkOp(link_id=link.id, to_registrar_id=key),
                    f"merge #{duplicate}: re-point link #{link.id} "
                    f"(company #{link.company_id}) -> {_fmt_key(key)}",
                )
            else:
                if k_row.deleted_at:
                    # A-1 (§4.1.1 gap, audit #4): K's row for the company is
                    # soft-deleted while D's is active — reactivate K's row
                    # keeping D's role, so the merge never leaves the company
                    # with fewer active links, then retire D's row.
                    self._add(
                        EnsurePrimaryLinkOp(company_id=link.company_id,
                                            registrar_key=key,
                                            link_id=k_row.id, role=link.role),
                        f"merge #{duplicate}: reactivate link #{k_row.id} for "
                        f"company #{link.company_id} with role {link.role!r}",
                    )
                # K has a row (active or reactivated) => D's row is retired,
                # never a second row for the pair (F4 / §4.1.1).
                self._add(
                    SoftDeleteLinkOp(link_id=link.id),
                    f"merge #{duplicate}: soft-delete link #{link.id} "
                    f"(company #{link.company_id}, {_fmt_key(key)} already linked)",
                )

        # 2. legacy FK companies.registrar_id = D => K
        for company in list(self.snap.companies):
            if company.deleted_at or company.registrar_id != duplicate:
                continue
            self._add(
                UpdateCompanyOp(company_id=company.id,
                                changes={"registrar_id": key}),
                f"company #{company.id}: registrar_id #{duplicate} -> {_fmt_key(key)}",
            )

        # 3. registrar_requirements.registrar_id = D => K (documents follow)
        for requirement in list(self.snap.requirements):
            if requirement.deleted_at or requirement.registrar_id != duplicate:
                continue
            self._add(
                RepointRequirementOp(requirement_id=requirement.id,
                                     to_registrar_id=key),
                f"requirement #{requirement.id}: registrar #{duplicate} -> {_fmt_key(key)}",
            )

        # 4. active contact fields move to K unless K has the same value
        #    (_values_for reads the working copy, so a field moved for an
        #    earlier duplicate is already counted here)
        values = self._values_for(key)
        for field_row in list(self.snap.fields):
            if field_row.registrar_id != duplicate or field_row.deleted_at:
                continue
            normalised = normalise(field_row.field_value, field_row.field_type)
            if normalised in values:
                continue
            values.add(normalised)
            self._add(
                MoveFieldOp(field_id=field_row.id, to_registrar_id=key),
                f"field #{field_row.id}: registrar #{duplicate} -> {_fmt_key(key)}",
            )

    def _build_contacts(self) -> None:
        """Spec §4.2 (file fields + legacy fills) and §4.3 (Entered manually)."""
        for entry in self.research.registrars:
            self._contacts_for(entry)

    def _contacts_for(self, entry: dict) -> None:
        slug = entry["slug"]
        key = self.targets[slug]
        resolved = self._key_id(key)
        # A-6: a ("new", slug) target already has its working row after
        # _create_new_registrars, so K's columns are read the same way for an
        # existing and for a brand-new registrar.
        k_row = self.snap.registrars.get(resolved)
        head_office = entry.get("head_office") or {}
        offices = list(entry.get("offices") or [])

        existing = [f for f in self.snap.fields
                    if f.registrar_id == resolved and not f.deleted_at]
        values = self._values_for(key)
        # A-4 (audit #7): base = max(existing active sort_order); the head
        # office takes base+10 and everything after it steps by 10.
        base = max((f.sort_order for f in existing), default=0)
        next_order = base + 10

        planned = []                       # [(sort_order, type, value, label)]

        # head office address sorts first, right after the existing fields
        head_value, head_label = self._head_office(head_office, offices)
        if head_value and normalise(head_value, "address") not in values:
            values.add(normalise(head_value, "address"))
            planned.append((next_order, "address", head_value, head_label))
            next_order += 10

        def stage(field_type, value, label):
            nonlocal next_order
            if not value:
                return
            normalised = normalise(value, field_type)
            if normalised in values:
                return                       # K already shows this value
            values.add(normalised)
            planned.append((next_order, field_type, value, label))
            next_order += 10

        # phones
        for phone in entry.get("phones") or []:
            stage("phone", phone.get("e164"), phone_label(phone))
        # emails: only show_on_page
        for email in entry.get("emails") or []:
            if not email.get("show_on_page"):
                continue
            stage("email", email.get("address"), email_label(email))
        # website / portals: safe_to_link gates the field type
        website = entry.get("website")
        website_spec = website_field(website)
        if website_spec:
            stage(website_spec[0], website.get("url"), website_spec[1])
        for portal in entry.get("portals") or []:
            portal_spec = portal_field(portal)
            if portal_spec:
                stage(portal_spec[0], portal.get("url"), portal_spec[1])
        # other offices: show_on_page, never the "Group ..." ones
        for office in offices:
            if office.get("is_head_office"):
                continue
            if str(office.get("type") or "").startswith("Group"):
                continue
            if not office.get("show_on_page"):
                continue
            stage("address", office.get("address"), office_label(office, head_office))

        # §4.3: hand-entered legacy values stay visible as "Entered manually"
        legacy_sources = []
        if k_row is not None:
            legacy_sources.extend((col, getattr(k_row, col))
                                  for col in LEGACY_COLUMNS if getattr(k_row, col))
        for duplicate in self.dup_legacy.get(key, []):
            legacy_sources.extend((col, getattr(duplicate, col))
                                  for col in LEGACY_COLUMNS if getattr(duplicate, col))
        for column, value in legacy_sources:
            stage(column, value, "Entered manually")

        for sort_order, field_type, value, label in planned:
            self._add(
                CreateFieldOp(registrar_key=key, field_type=field_type,
                              field_value=value, label=label, sort_order=sort_order),
                f"registrar {_fmt_key(key)}: add {field_type} field {value!r} "
                f"(label {label!r}, sort {sort_order})",
            )

        # §4.2: legacy columns are filled only when NULL, never overwritten
        current = {
            "email": k_row.email if k_row else None,
            "phone": k_row.phone if k_row else None,
            "address": k_row.address if k_row else None,
            "website": k_row.website if k_row else None,
        }
        fills = {}
        # A-3 (audit #6): the file fills a NULL legacy column only with a
        # value that is also stored (or already present) as a visible field on
        # K — `values` holds exactly those: the active fields K has, the ones
        # the merge moved in and the ones staged above in this very call.
        if (not current["email"] and entry.get("primary_email")
                and normalise(entry["primary_email"], "email") in values):
            fills["email"] = entry["primary_email"]
        if (not current["phone"] and entry.get("primary_phone")
                and normalise(entry["primary_phone"], "phone") in values):
            fills["phone"] = entry["primary_phone"]
        if (not current["address"] and head_office.get("address")
                and normalise(head_office["address"], "address") in values):
            fills["address"] = head_office["address"]
        if (not current["website"] and website_spec
                and website_spec[0] == "website"
                and normalise(website.get("url"), "website") in values):
            fills["website"] = website.get("url")
        if fills:
            self._add(
                UpdateRegistrarOp(registrar_key=key, changes=dict(fills)),
                f"registrar {_fmt_key(key)}: fill NULL legacy columns "
                f"{', '.join(sorted(fills))}",
            )

    @staticmethod
    def _head_office(head_office: dict, offices: list):
        """The head office address field: the office entry when it is visible,
        otherwise head_office.address (AC-7 suffix comes from the confidence)."""
        head_entry = None
        for office in offices:
            if office.get("is_head_office"):
                head_entry = office
                break
        if head_entry is not None:
            if not head_entry.get("show_on_page"):
                return (None, None)
            if str(head_entry.get("type") or "").startswith("Group"):
                return (None, None)
            return (head_entry.get("address"),
                    office_label(head_entry, head_office))
        if head_office.get("address"):
            fallback = {"type": "Head office", "is_head_office": True,
                        "confidence": head_office.get("confidence")}
            return (head_office.get("address"), office_label(fallback, head_office))
        return (None, None)

    def _build_links(self) -> None:
        """Spec §4.4: firm mappings relink, weak ones are held back."""
        by_ticker = {
            str(company.ticker).upper(): company
            for company in self.snap.companies
            if not company.deleted_at and company.ticker
        }
        for entry in self.research.registrars:
            slug = entry["slug"]
            key = self.targets[slug]
            for client in entry.get("clients") or []:
                ticker = client.get("ticker")
                company_name = client.get("company")
                if not ticker:
                    self.plan.unmatched.append({
                        "ticker": None, "company": company_name,
                        "registrar": slug, "reason": "no ticker in the file",
                    })
                    continue
                company = by_ticker.get(str(ticker).upper())
                if company is None:
                    self.plan.unmatched.append({
                        "ticker": ticker, "company": company_name,
                        "registrar": slug, "reason": "ticker not in companies",
                    })
                    continue
                if classify(client) == "weak":
                    self.plan.held_back.append({
                        "ticker": company.ticker, "company": company.name,
                        "registrar": slug,
                        "confidence": client.get("mapping_confidence"),
                        "flag": client.get("mapping_flag"),
                    })
                    continue
                self._firm_link(company, key)

    def _firm_link(self, company: CompanyRow, key) -> None:
        resolved = self._key_id(key)

        # 1. the canonical's own active primary row stays; every other active
        #    primary of the company is retired (§4.4). The lookup goes through
        #    the working copy, so a row an earlier op repointed or reactivated
        #    is already excluded here (A-6: no second change on one row).
        active_primaries = [link for link in self.snap.links
                            if link.company_id == company.id
                            and not link.deleted_at and link.role == "primary"]
        for link in active_primaries:
            if link.registrar_id == resolved:
                continue                    # already points at the canonical
            self._add(
                SoftDeleteLinkOp(link_id=link.id),
                f"company #{company.id}: soft-delete primary link #{link.id} "
                f"(registrar #{link.registrar_id})",
            )

        # 2. the company must hold one active (company, K) row: reactivate the
        #    soft-deleted one (A-2: deleted_at=NULL and role='primary' land in
        #    the same operation), otherwise insert one — never a second row (F4)
        if company.id not in self._companies_at(key, active_only=True):
            soft_deleted_row = self._row_for(company.id, key, soft_deleted=True)
            if soft_deleted_row is not None:
                self._add(
                    EnsurePrimaryLinkOp(company_id=company.id, registrar_key=key,
                                        link_id=soft_deleted_row.id,
                                        role="primary"),
                    f"company #{company.id}: reactivate primary link "
                    f"#{soft_deleted_row.id} -> {_fmt_key(key)}",
                )
            else:
                self._add(
                    CreateLinkOp(company_id=company.id, registrar_key=key),
                    f"company #{company.id}: create primary link -> {_fmt_key(key)}",
                )

        # 3. the legacy FK the registrar detail page reads (F1)
        if company.registrar_id != resolved:
            self._add(
                UpdateCompanyOp(company_id=company.id,
                                changes={"registrar_id": key}),
                f"company #{company.id}: registrar_id "
                f"{company.registrar_id} -> {_fmt_key(key)}",
            )

    def _finish(self) -> None:
        # without_contact_record rows: reported, never written (§4.4)
        for block in self.research.without_contact_record or []:
            for client in block.get("clients") or []:
                self.plan.without_contact_record.append({
                    "ticker": client.get("ticker"),
                    "company": client.get("company"),
                    "registrar_as_recorded": block.get("registrar_as_recorded"),
                    "reason": block.get("reason"),
                })

        counts = {key: 0 for key in COUNT_KEYS}
        for op in self.plan.ops:
            if isinstance(op, CreateRegistrarOp):
                counts["registrars_created"] += 1
            elif isinstance(op, RenameRegistrarOp):
                counts["registrars_renamed"] += 1
            elif isinstance(op, SoftDeleteRegistrarOp):
                counts["registrars_soft_deleted"] += 1
            elif isinstance(op, CreateFieldOp):
                counts["fields_added"] += 1
            elif isinstance(op, MoveFieldOp):
                counts["fields_moved"] += 1
            elif isinstance(op, UpdateRegistrarOp):
                counts["legacy_columns_filled"] += len(
                    set(op.changes) & set(LEGACY_COLUMNS))
            elif isinstance(op, CreateLinkOp):
                counts["links_created"] += 1
            elif isinstance(op, EnsurePrimaryLinkOp):
                counts["links_reactivated"] += 1
            elif isinstance(op, SoftDeleteLinkOp):
                counts["links_soft_deleted"] += 1
            elif isinstance(op, RepointLinkOp):
                counts["links_repointed"] += 1
            elif isinstance(op, RepointRequirementOp):
                counts["requirements_repointed"] += 1
            elif isinstance(op, UpdateCompanyOp):
                counts["companies_registrar_changed"] += 1
        counts["registrars_merged"] = self._merged
        self.plan.counts = counts
        self.plan.report_counts = {
            "held_back": len(self.plan.held_back),
            "unmatched": len(self.plan.unmatched),
            "without_contact_record": len(self.plan.without_contact_record),
        }

        for held in self.plan.held_back:
            self.plan.report_lines.append(
                f"held back (weak): {held['ticker']} ({held['company']}) for "
                f"{held['registrar']} — no link change, Product Owner decides "
                f"[{held.get('confidence')}/{held.get('flag')}]"
            )
        for unmatched in self.plan.unmatched:
            ticker = unmatched["ticker"] or "(no ticker)"
            self.plan.report_lines.append(
                f"unmatched: {ticker} ({unmatched['company']}) for "
                f"{unmatched['registrar']} — {unmatched['reason']}, no link written"
            )
        for record in self.plan.without_contact_record:
            ticker = record["ticker"] or "(no ticker)"
            self.plan.report_lines.append(
                f"without contact record: {ticker} ({record['company']}) for "
                f"{record['registrar_as_recorded']} — {record['reason']}, "
                "no company created"
            )


def build_plan(research: Research, snapshot: Snapshot, resolution_table: dict) -> Plan:
    """Build the full plan. Pure: no DB access; raises ResolutionError (§3)."""
    return _Planner(research, snapshot, resolution_table).run()


def format_plan(plan: Plan) -> str:
    """Readable plan + counts block + the informational report."""
    out = ["== registrar research import: plan =="]
    if plan.lines:
        out.extend(f"  {line}" for line in plan.lines)
    else:
        out.append("  (no changes — the data already matches the plan)")
    out.append("")
    out.append("== counts ==")
    out.extend(f"  {line}" for line in plan.counts_block())
    if plan.report_lines:
        out.append("")
        out.append("== report (informational, no changes) ==")
        out.extend(f"  {line}" for line in plan.report_lines)
    return "\n".join(out)


# ─── DB layer ──────────────────────────────────────────────────────────────────

def _table(name: str):
    """Table objects, imported lazily: the pure layer must import cleanly."""
    from app.models import (
        Company, CompanyRegistrar, Registrar, RegistrarContactField,
        RegistrarRequirement,
    )
    return {
        "registrars": Registrar.__table__,
        "registrar_contact_fields": RegistrarContactField.__table__,
        "company_registrars": CompanyRegistrar.__table__,
        "companies": Company.__table__,
        "registrar_requirements": RegistrarRequirement.__table__,
    }[name]


def _resolved(key, created: dict) -> int:
    """int id, or the id a ("new", slug) op got during this apply."""
    if isinstance(key, int):
        return key
    return created[key]


def _resolve_changes(changes: dict, created: dict) -> dict:
    """A change value may be a ("new", slug) key: resolve it to the real id."""
    return {
        name: (_resolved(value, created) if isinstance(value, tuple) else value)
        for name, value in changes.items()
    }


async def load_snapshot(session: AsyncSession) -> Snapshot:
    """Every row the plan needs (soft-deleted rows included, §3 checks)."""
    registrars = {}
    for row in (await session.execute(select(_table("registrars")))).mappings():
        registrars[row["id"]] = RegistrarRow(
            id=row["id"], name=row["name"], email=row["email"],
            phone=row["phone"], address=row["address"],
            website=row["website"], response_rating=row["response_rating"],
            notes=row["notes"], status=row["status"],
            jurisdiction=row["jurisdiction"], deleted_at=row["deleted_at"],
        )
    fields = [FieldRow(
        id=row["id"], registrar_id=row["registrar_id"],
        field_type=row["field_type"], field_value=row["field_value"],
        label=row["label"], sort_order=row["sort_order"],
        deleted_at=row["deleted_at"],
    ) for row in (await session.execute(select(_table("registrar_contact_fields")))).mappings()]
    links = [LinkRow(
        id=row["id"], company_id=row["company_id"],
        registrar_id=row["registrar_id"], role=row["role"],
        deleted_at=row["deleted_at"],
    ) for row in (await session.execute(select(_table("company_registrars")))).mappings()]
    companies = [CompanyRow(
        id=row["id"], ticker=row["ticker"], name=row["name"],
        registrar_id=row["registrar_id"], deleted_at=row["deleted_at"],
    ) for row in (await session.execute(select(_table("companies")))).mappings()]
    requirements = [RequirementRow(
        id=row["id"], registrar_id=row["registrar_id"],
        deleted_at=row["deleted_at"],
    ) for row in (await session.execute(select(_table("registrar_requirements")))).mappings()]
    return Snapshot(
        registrars=registrars, fields=fields, links=links,
        companies=companies, requirements=requirements,
    )


async def _previous_values(session, table_name, row_id, keys) -> dict:
    """The values a row holds *before* an update, so undo can restore them
    (updated_at is recorded too: nothing may drift after an undo)."""
    table = _table(table_name)
    columns = list(keys)
    if "updated_at" in table.c.keys() and "updated_at" not in columns:
        columns.append("updated_at")
    stmt = select(*[table.c[name] for name in columns]).where(table.c.id == row_id)
    row = (await session.execute(stmt)).one()
    return {name: row._mapping[name] for name in columns}


async def _update(session, table_name, row_id, values, record) -> None:
    table = _table(table_name)
    previous = await _previous_values(session, table_name, row_id, tuple(values))
    await session.execute(update(table).where(table.c.id == row_id).values(**values))
    record.add_update(table_name, row_id, previous)


async def apply_plan(session: AsyncSession, plan: Plan) -> UndoRecord:
    """Apply every op of the plan in the caller's transaction. Never commits."""
    database = (await session.execute(text("select current_database()"))).scalar_one()
    record = UndoRecord(
        database=database,
        applied_at=datetime.now(timezone.utc).isoformat(),
        counts=dict(plan.counts),
    )
    created: dict = {}

    for op in plan.ops:
        if isinstance(op, CreateRegistrarOp):
            table = _table("registrars")
            row_id = (await session.execute(
                insert(table).values(
                    name=op.name, jurisdiction=op.jurisdiction, status=op.status,
                ).returning(table.c.id)
            )).scalar_one()
            created[op.key] = row_id
            record.add_insert("registrars", row_id)
        elif isinstance(op, RenameRegistrarOp):
            await _update(session, "registrars", op.registrar_id,
                          {"name": op.new_name}, record)
        elif isinstance(op, UpdateRegistrarOp):
            await _update(session, "registrars",
                          _resolved(op.registrar_key, created),
                          _resolve_changes(op.changes, created), record)
        elif isinstance(op, SoftDeleteRegistrarOp):
            await _update(session, "registrars", op.registrar_id,
                          {"deleted_at": func.now()}, record)
        elif isinstance(op, MoveFieldOp):
            await _update(session, "registrar_contact_fields", op.field_id,
                          {"registrar_id": _resolved(op.to_registrar_id, created)},
                          record)
        elif isinstance(op, CreateFieldOp):
            table = _table("registrar_contact_fields")
            row_id = (await session.execute(
                insert(table).values(
                    registrar_id=_resolved(op.registrar_key, created),
                    field_type=op.field_type, field_value=op.field_value,
                    label=op.label, sort_order=op.sort_order,
                ).returning(table.c.id)
            )).scalar_one()
            record.add_insert("registrar_contact_fields", row_id)
        elif isinstance(op, SoftDeleteLinkOp):
            await _update(session, "company_registrars", op.link_id,
                          {"deleted_at": func.now()}, record)
        elif isinstance(op, EnsurePrimaryLinkOp):
            if op.link_id is None:
                table = _table("company_registrars")
                row = (await session.execute(
                    select(table).where(
                        table.c.company_id == op.company_id,
                        table.c.registrar_id == _resolved(op.registrar_key, created),
                        table.c.deleted_at.isnot(None),
                    )
                )).mappings().first()
                op = EnsurePrimaryLinkOp(company_id=op.company_id,
                                         registrar_key=op.registrar_key,
                                         link_id=row["id"] if row else None,
                                         role=op.role)
            if op.link_id is None:
                table = _table("company_registrars")
                row_id = (await session.execute(
                    insert(table).values(
                        company_id=op.company_id,
                        registrar_id=_resolved(op.registrar_key, created),
                        role=op.role,
                    ).returning(table.c.id)
                )).scalar_one()
                record.add_insert("company_registrars", row_id)
            else:
                # A-2: deleted_at=NULL and role land in the same statement —
                # a firm mapping reactivates the row as a primary (A-1 keeps
                # D's role for the merge reactivation).
                await _update(session, "company_registrars", op.link_id,
                              {"deleted_at": None, "role": op.role}, record)
        elif isinstance(op, CreateLinkOp):
            table = _table("company_registrars")
            row_id = (await session.execute(
                insert(table).values(
                    company_id=op.company_id,
                    registrar_id=_resolved(op.registrar_key, created),
                    role=op.role,
                ).returning(table.c.id)
            )).scalar_one()
            record.add_insert("company_registrars", row_id)
        elif isinstance(op, RepointLinkOp):
            await _update(session, "company_registrars", op.link_id,
                          {"registrar_id": _resolved(op.to_registrar_id, created)},
                          record)
        elif isinstance(op, RepointRequirementOp):
            await _update(session, "registrar_requirements", op.requirement_id,
                          {"registrar_id": _resolved(op.to_registrar_id, created)},
                          record)
        elif isinstance(op, UpdateCompanyOp):
            await _update(session, "companies", op.company_id,
                          _resolve_changes(op.changes, created), record)
        else:                                            # pragma: no cover
            raise ResearchImportError(f"unknown operation: {op!r}")

    await session.flush()
    return record


async def undo(session: AsyncSession, record: UndoRecord) -> None:
    """Restore every touched row, soft-delete what was inserted, reactivate the
    merged duplicates. Never commits (the caller owns the transaction)."""
    for entry in reversed(record.entries):
        table = _table(entry["table"])
        if entry.get("inserted"):
            await session.execute(
                update(table).where(table.c.id == entry["id"])
                .values(deleted_at=func.now())
            )
        else:
            values = {key: _decode(value)
                      for key, value in entry.get("previous", {}).items()}
            if values:
                await session.execute(
                    update(table).where(table.c.id == entry["id"]).values(**values)
                )
    await session.flush()


# ─── CLI ────────────────────────────────────────────────────────────────────────

def _redact(output: str) -> str:
    """Never print DATABASE_URL or its password."""
    output = re.sub(r"(://[^:/@\s]+):[^@\s]+@", r"\1:***@", output)
    return re.sub(r"(password=)[^\s&]+", r"\1***", output, flags=re.IGNORECASE)


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="import_registrar_research",
        description=(
            "Import the researched registrar contacts (F-026c). The default "
            "mode is a read-only preview; --apply needs --confirm-db and runs "
            "in one transaction."
        ),
    )
    parser.add_argument(
        "--research", metavar="PATH", default=None,
        help="research markdown file (default: "
             "docs/registrars/registrars_contact_details_final.md)",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="write the plan in one transaction (requires --confirm-db "
             "and --undo-out)",
    )
    parser.add_argument(
        "--confirm-db", metavar="NAME", default=None,
        help="database name; must equal select current_database()",
    )
    parser.add_argument(
        "--undo-out", metavar="PATH", default=None,
        help="where the undo record of --apply is written BEFORE the commit; "
             "'-' prints it between the F026C UNDO JSON markers (container "
             "runs, where only stdout reaches the host)",
    )
    parser.add_argument(
        "--undo", metavar="FILE", default=None,
        help="undo file of a previous --apply (requires --confirm-db)",
    )
    return parser


def _load_research(args, research_text: str | None) -> Research:
    if research_text is not None:
        return parse_research(text=research_text)
    path = Path(args.research) if args.research else _default_research_path()
    if not path.exists():
        raise ResearchImportError(f"research file not found: {path}")
    return parse_research(path)


async def _connected_database(session) -> str:
    return (await session.execute(text("select current_database()"))).scalar_one()


async def _run_preview(engine, research: Research,
                       resolution_table: dict | None = None) -> int:
    """AC-1: read-only transaction, print the plan and the counts.

    ``resolution_table`` defaults to the production §3 table; the integration
    test passes its own ids so the real entry point can run against the
    fixture rows (the CLI never passes it).
    """
    async with engine.connect() as connection:
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            async with session.begin():
                # first statement of the transaction: Postgres itself then
                # rejects every write with SQLSTATE 25006
                await session.execute(text("SET TRANSACTION READ ONLY"))
                snapshot = await load_snapshot(session)
                plan = build_plan(research, snapshot,
                                  resolution_table or RESOLUTION_TABLE)
                print(format_plan(plan))
        finally:
            await session.close()
    return 0


async def _apply_transaction(session, research: Research, confirm_db: str,
                             undo_out: str):
    """The whole body of the apply transaction, undo record included (A-7 /
    AC-17): the record is written while the transaction is still open, so a
    failing writer makes ``session.begin()`` roll the apply back."""
    connected = await _connected_database(session)
    check_confirm_db(confirm_db, connected)                 # before any write
    snapshot = await load_snapshot(session)
    plan = build_plan(research, snapshot, RESOLUTION_TABLE)
    print(format_plan(plan))
    record = await apply_plan(session, plan)
    where = _write_undo(record, undo_out)                   # BEFORE the COMMIT
    return record, where


async def _run_apply(engine, research: Research, confirm_db: str,
                     undo_out: str) -> int:
    """AC-14/AC-15/AC-17: one transaction, all or nothing."""
    async with engine.connect() as connection:
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            async with session.begin():
                record, where = await _apply_transaction(
                    session, research, confirm_db, undo_out)
            # session.begin() commits here — and only because _write_undo
            # returned; on any error above (including the writer) it rolls back
        finally:
            await session.close()
    print(f"applied in one transaction to {record.database}; undo file: {where}")
    return 0


async def _run_undo(db_url: str, args) -> int:
    path = Path(args.undo)
    if not path.exists():
        raise ResearchImportError(f"undo file not found: {path}")
    record = UndoRecord.from_json(json.loads(path.read_text(encoding="utf-8")))
    engine = create_async_engine(db_url, poolclass=NullPool)
    try:
        async with engine.connect() as connection:
            session = AsyncSession(bind=connection, expire_on_commit=False)
            try:
                async with session.begin():
                    connected = await _connected_database(session)
                    check_confirm_db(args.confirm_db, connected)
                    if record.database and record.database != connected:
                        raise ConfirmDatabaseError(
                            f"the undo file was written against "
                            f"{record.database!r}, connected to {connected!r}"
                        )
                    await undo(session, record)
                    print(f"undid {len(record.entries)} row changes on {connected}")
            finally:
                await session.close()
    finally:
        await engine.dispose()
    return 0


UNDO_JSON_BEGIN = "=== F026C UNDO JSON BEGIN ==="
UNDO_JSON_END = "=== F026C UNDO JSON END ==="


def _write_undo(record: UndoRecord, undo_out: str) -> str:
    """A-7 (audit #2): write the undo record BEFORE the commit of the apply
    transaction, so every committed run has a record that covers it.

    ``undo_out`` is a file path, or ``-`` for stdout between
    :data:`UNDO_JSON_BEGIN` / :data:`UNDO_JSON_END` — the production run in
    the container, where only stdout reaches the host. Any failure here
    propagates out of the transaction block, which rolls the apply back
    (AC-17). Returns where the record went, for the final log line."""
    payload = {"feature": "F-026c", **record.to_json()}
    blob = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if undo_out == "-":
        print(UNDO_JSON_BEGIN)
        print(blob, end="")
        print(UNDO_JSON_END)
        return "stdout (between the F026C UNDO JSON markers)"
    path = Path(undo_out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(blob, encoding="utf-8")
    return str(path)


async def cli(argv: list, research_text: str | None = None) -> int:
    """Entry used by __main__ (and by the container's stdin preview).

    When ``research_text`` is given it is parsed instead of ``--research``.
    Returns a process exit code; never raises for expected failures.
    """
    parser = _argument_parser()
    try:
        args = parser.parse_args([str(item) for item in argv])
    except SystemExit as exc:                     # --help (0) / usage error (2)
        return int(exc.code or 0)

    if args.apply and args.undo:
        print("error: --apply and --undo are mutually exclusive", file=sys.stderr)
        return 2
    if args.apply and not args.undo_out:
        # A-7: an apply without a place to put the undo record must not run
        print("error: --apply requires --undo-out <path|-> "
              "(the undo record is written before the commit)",
              file=sys.stderr)
        return 2
    if (args.apply or args.undo) and not args.confirm_db:
        print("error: --confirm-db <dbname> is required with --apply/--undo",
              file=sys.stderr)
        return 2
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("error: DATABASE_URL is not set; refusing to run", file=sys.stderr)
        return 3

    engine = None
    try:
        if args.undo:
            return await _run_undo(db_url, args)

        research = _load_research(args, research_text)
        engine = create_async_engine(db_url, poolclass=NullPool)
        if args.apply:
            return await _run_apply(engine, research, args.confirm_db,
                                    args.undo_out)
        return await _run_preview(engine, research)
    except (ConfirmDatabaseError, ParseError, ResolutionError,
            ResearchImportError) as exc:
        print(f"error: {_redact(str(exc))}", file=sys.stderr)
        return 2
    except Exception as exc:                      # connection errors, SQL errors
        print(f"error: {_redact(f'{type(exc).__name__}: {exc}')}",
              file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            await engine.dispose()


async def amain(argv: list) -> int:
    """Backwards-compatible wrapper around :func:`cli`."""
    return await cli(argv)


if __name__ == "__main__" and not globals().get("_F026C_EMBEDDED"):
    sys.exit(asyncio.run(cli(sys.argv[1:])))
