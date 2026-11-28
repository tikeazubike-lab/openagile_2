# backend/tests/unit/test_import_registrar_research.py
"""
F-026c — unit tests for the registrar research import (pure layer).

No database: parse_research / classify / label helpers / normalisation /
build_plan run against the hand-made fixture
tests/fixtures/registrar_research_sample.md and an in-memory Snapshot.

Trace on every test:
  # Spec: F-026c-registrar-research-import.md | AC-N
"""
import asyncio
import json
from collections import defaultdict
from pathlib import Path

import pytest

# `imp` gives the tests the module object itself: A-6/A-7 helpers that do not
# exist yet are reached through it (imp.apply_ops_to_snapshot, imp._write_undo),
# so those tests fail on their own instead of breaking the whole file at import.
import scripts.import_registrar_research as imp
from scripts.import_registrar_research import (
    ConfirmDatabaseError,
    CompanyRow,
    CreateFieldOp,
    CreateLinkOp,
    CreateRegistrarOp,
    EnsurePrimaryLinkOp,
    FieldRow,
    LinkRow,
    MoveFieldOp,
    ParseError,
    RegistrarRow,
    RenameRegistrarOp,
    RepointLinkOp,
    RepointRequirementOp,
    RequirementRow,
    ResolutionEntry,
    ResolutionError,
    Snapshot,
    SoftDeleteLinkOp,
    SoftDeleteRegistrarOp,
    UndoRecord,
    UpdateCompanyOp,
    UpdateRegistrarOp,
    amain,
    build_plan,
    check_confirm_db,
    classify,
    email_label,
    normalise,
    office_label,
    parse_research,
    phone_label,
    portal_field,
    website_field,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "registrar_research_sample.md"


# ─── fixture builders (plain dataclasses, no DB) ───────────────────────────────

def _research():
    return parse_research(FIXTURE)


def _resolution_table():
    return {
        "alpha": ResolutionEntry(
            slug="alpha", canonical=1, duplicates=(3,),
            final_name="Alpha Registrars Limited",
        ),
        "newbies": ResolutionEntry(
            slug="newbies", canonical=None, duplicates=(),
            final_name="Newbies Registrars Limited",
        ),
    }


def _snapshot():
    """Current rows exactly as load_snapshot() would return them."""
    return Snapshot(
        registrars={
            1: RegistrarRow(
                id=1, name="Alpha Registrars Nigeria Limited",
                email=None, phone="01 555 0100", address=None, website=None,
                response_rating=None, notes=None,
                status="active", jurisdiction="nigeria", deleted_at=None,
            ),
            2: RegistrarRow(
                id=2, name="Beta Registrars",
                email=None, phone=None, address=None, website=None,
                response_rating=None, notes=None,
                status="active", jurisdiction="nigeria", deleted_at=None,
            ),
            3: RegistrarRow(
                id=3, name="Alpha Old Registrars Limited",
                email="old@alpha.example", phone=None, address=None, website=None,
                response_rating=4, notes="hand notes",
                status="active", jurisdiction="nigeria", deleted_at=None,
            ),
        },
        fields=[
            FieldRow(id=101, registrar_id=1, field_type="phone",
                     field_value="+234 801 234 5678", label="switchboard",
                     sort_order=10, deleted_at=None),
            FieldRow(id=102, registrar_id=3, field_type="other",
                     field_value="Fax 01-555-0100", label="fax",
                     sort_order=1, deleted_at=None),
        ],
        links=[
            LinkRow(id=201, company_id=101, registrar_id=1, role="primary",
                    deleted_at=None),
            LinkRow(id=202, company_id=102, registrar_id=3, role="primary",
                    deleted_at=None),
            LinkRow(id=203, company_id=101, registrar_id=2, role="primary",
                    deleted_at=None),
        ],
        companies=[
            CompanyRow(id=101, ticker="ALPHA", registrar_id=1, deleted_at=None),
            CompanyRow(id=102, ticker="WEAKCO", registrar_id=3, deleted_at=None),
            CompanyRow(id=103, ticker="NEWBIE", registrar_id=None, deleted_at=None),
            CompanyRow(id=104, ticker="UNVCO", registrar_id=None, deleted_at=None),
        ],
        requirements=[
            RequirementRow(id=301, registrar_id=3, deleted_at=None),
        ],
    )


def _snapshot_ghost():
    """_snapshot() plus the rows audits #1 and #4 were about (A-1/A-6):

    * ``GHOST`` (company 105) is firmly mapped to canonical #1 by the file,
      duplicate #3 still holds its ACTIVE link, and canonical #1's own row for
      the company is soft-deleted — the merge must reactivate #1's row
      (audit #4) and the firm mapping must not add a second change (audit #1).
    * ``OTHERCO`` (company 106) is not in the file at all: its link to the
      duplicate is active with role ``co_registrar`` while #1's row is
      soft-deleted — A-1 reactivates #1's row keeping D's role.
    """
    snapshot = _snapshot()
    snapshot.companies.extend([
        CompanyRow(id=105, ticker="GHOST", name="Ghost Co Plc",
                   registrar_id=3, deleted_at=None),
        CompanyRow(id=106, ticker="OTHERCO", name="Other Co Plc",
                   registrar_id=3, deleted_at=None),
    ])
    snapshot.links.extend([
        LinkRow(id=204, company_id=105, registrar_id=3, role="primary",
                deleted_at=None),
        LinkRow(id=205, company_id=105, registrar_id=1, role="primary",
                deleted_at=True),
        LinkRow(id=206, company_id=106, registrar_id=3, role="co_registrar",
                deleted_at=None),
        LinkRow(id=207, company_id=106, registrar_id=1, role="primary",
                deleted_at=True),
    ])
    return snapshot


def _build():
    return build_plan(_research(), _snapshot(), _resolution_table())


def _ops(plan, cls):
    return [op for op in plan.ops if isinstance(op, cls)]


def _fields(plan, registrar_key):
    return [op for op in _ops(plan, CreateFieldOp)
            if op.registrar_key == registrar_key]


def _field_values(ops):
    return [op.field_value for op in ops]


@pytest.fixture
def research():
    return _research()


@pytest.fixture
def resolution_table():
    return _resolution_table()


@pytest.fixture
def snapshot():
    return _snapshot()


# ─── parsing ────────────────────────────────────────────────────────────────────

def test_parse_research_reads_the_single_json_block():
    # Spec: F-026c-registrar-research-import.md | AC-1
    """The data block is the single fenced json block in the file."""
    research = parse_research(FIXTURE)
    assert [r["slug"] for r in research.registrars] == ["alpha", "newbies"]
    assert research.registrars[0]["clients"][0]["ticker"] == "ALPHA"
    assert len(research.without_contact_record) == 1


def test_parse_research_reads_the_same_result_from_research_text():
    # Spec: F-026c-registrar-research-import.md | AC-1
    """cli(argv, research_text=...) parses the file content instead of the
    path (container preview, stdin only): the Research is identical either way
    (``source`` is excluded from the comparison — it only says where the text
    came from)."""
    from_text = parse_research(text=FIXTURE.read_text(encoding="utf-8"))
    from_path = parse_research(FIXTURE)
    assert from_text == from_path
    assert from_text.registrars == from_path.registrars
    assert from_text.without_contact_record == from_path.without_contact_record


@pytest.mark.parametrize("body", [
    "no fenced block at all",
    "```json\n{\"a\": 1}\n```\n\n```json\n{\"b\": 2}\n```\n",
    "```json\n{not json}\n```\n",
])
def test_parse_research_rejects_a_file_without_exactly_one_json_block(body, tmp_path):
    # Spec: F-026c-registrar-research-import.md | AC-1
    bad = tmp_path / "bad.md"
    bad.write_text(body, encoding="utf-8")
    with pytest.raises(ParseError):
        parse_research(bad)


# ─── firm / weak classification (§4.4) ─────────────────────────────────────────

@pytest.mark.parametrize("client,expected", [
    ({"mapping_confidence": "High", "mapping_flag": "OK"}, "firm"),
    ({"mapping_confidence": "Medium", "mapping_flag": "SINGLE-SOURCE"}, "firm"),
    ({"mapping_confidence": "Medium", "mapping_flag": "STALE"}, "firm"),
    ({"mapping_confidence": "Low", "mapping_flag": "SINGLE-SOURCE"}, "weak"),
    ({"mapping_confidence": "Low", "mapping_flag": "OK"}, "weak"),
    ({"mapping_confidence": "Medium", "mapping_flag": "UNVERIFIED"}, "weak"),
])
def test_classify_firm_and_weak(client, expected):
    # Spec: F-026c-registrar-research-import.md | AC-10
    """Low confidence or UNVERIFIED flag => weak (held back), else firm."""
    assert classify(client) == expected


# ─── normalisation (§4.1.4) ────────────────────────────────────────────────────

def test_normalise_casefolds_and_collapses_whitespace():
    # Spec: F-026c-registrar-research-import.md | AC-12
    assert normalise("  Alpha   Registrars\nLtd ") == "alpha registrars ltd"


def test_normalise_keeps_digits_only_for_phones():
    # Spec: F-026c-registrar-research-import.md | AC-12
    assert normalise("+234 (801) 234-5678", "phone") == "2348012345678"
    assert normalise("0801 234 5678", "phone") == "08012345678"


def test_normalise_none_is_empty_string():
    # Spec: F-026c-registrar-research-import.md | AC-12
    assert normalise(None) == ""


def test_plan_skips_a_value_the_registrar_already_has():
    # Spec: F-026c-registrar-research-import.md | AC-12
    """§4.1.4: file phone +2348012345678 equals the existing field
    "+234 801 234 5678" (digits only) => not stored twice."""
    plan = _build()
    assert "+2348012345678" not in _field_values(_fields(plan, 1))


# ─── label rules (§4.2) ────────────────────────────────────────────────────────

def test_phone_label_uses_file_label_or_phone_and_appends_warning():
    # Spec: F-026c-registrar-research-import.md | AC-7
    assert phone_label({"label": None, "warning": None}) == "Phone"
    assert phone_label({"label": "main line", "warning": None}) == "main line"
    assert phone_label({
        "label": "after hours",
        "warning": "answered by the group desk",
    }) == "after hours — answered by the group desk"


def test_phone_label_is_cut_to_100_chars():
    # Spec: F-026c-registrar-research-import.md | AC-7
    label = phone_label({"label": "main line", "warning": "w" * 300})
    assert len(label) == 100
    assert label.startswith("main line — ")


def test_email_label_uses_file_label_or_email():
    # Spec: F-026c-registrar-research-import.md | AC-6
    assert email_label({"label": None}) == "Email"
    assert email_label({"label": "back office"}) == "back office"
    assert len(email_label({"label": "x" * 300})) == 100


def test_website_rules_gate_field_type_on_safe_to_link():
    # Spec: F-026c-registrar-research-import.md | AC-5
    assert website_field({"url": "https://alpha.example",
                          "safe_to_link": False}) == (
        "other", "Website (not verified, copy manually)")
    assert website_field({"url": "https://alpha.example",
                          "safe_to_link": True}) == ("website", "Website")
    assert website_field({"url": None, "safe_to_link": True}) is None
    assert website_field(None) is None


def test_portal_rules_mirror_the_website_rules():
    # Spec: F-026c-registrar-research-import.md | AC-5
    assert portal_field({"url": "https://portal.alpha.example",
                         "description": None, "safe_to_link": False}) == (
        "other", "Online portal")
    assert portal_field({"url": "https://etransfer.alpha.example",
                         "description": "e-transfer portal",
                         "safe_to_link": True}) == ("website", "e-transfer portal")


@pytest.mark.parametrize("office,head_office,expect_suffix", [
    # AC-7 branch 1: head office confidence not High
    ({"type": "Head office", "is_head_office": True, "confidence": "Medium"},
     {"flag": "OK"}, True),
    # AC-7 branch 2: head office with flag CONFLICT / STALE
    ({"type": "Head office", "is_head_office": True, "confidence": "High"},
     {"flag": "CONFLICT"}, True),
    ({"type": "Head office", "is_head_office": True, "confidence": "High"},
     {"flag": "STALE"}, True),
    # High + OK: no suffix; the flag never applies to a branch office
    ({"type": "Head office", "is_head_office": True, "confidence": "High"},
     {"flag": "OK"}, False),
    ({"type": "Branch", "is_head_office": False, "confidence": "High"},
     {"flag": "CONFLICT"}, False),
    # a non-head office with Medium confidence still asks for confirmation
    ({"type": "Liaison office", "is_head_office": False,
      "confidence": "Medium"}, {"flag": "OK"}, True),
])
def test_office_label_please_confirm_suffix(office, head_office, expect_suffix):
    # Spec: F-026c-registrar-research-import.md | AC-7
    label = office_label(office, head_office)
    assert label.endswith("(please confirm)") is expect_suffix
    assert len(label) <= 100


# ─── plan building (AC-5, AC-6, AC-7, AC-10, AC-11) ────────────────────────────

def test_ac5_unsafe_website_is_stored_as_other_not_website():
    # Spec: F-026c-registrar-research-import.md | AC-5
    plan = _build()
    alpha = _fields(plan, 1)
    unsafe = [op for op in alpha if op.field_value == "https://alpha.example"]
    assert len(unsafe) == 1
    assert unsafe[0].field_type == "other"
    assert unsafe[0].label == "Website (not verified, copy manually)"
    # a safe portal on the same registrar keeps the linkable type
    safe = [op for op in alpha
            if op.field_value == "https://etransfer.alpha.example"]
    assert len(safe) == 1
    assert safe[0].field_type == "website"


def test_ac6_hidden_email_hidden_office_and_group_office_are_not_stored():
    # Spec: F-026c-registrar-research-import.md | AC-6
    plan = _build()
    values = _field_values(_ops(plan, CreateFieldOp))
    assert "backoffice@alpha.example" not in values      # show_on_page: false
    assert "4 Hidden Street, Lagos" not in values         # show_on_page: false
    assert "2 Group Road, Lagos" not in values            # type starts with Group
    assert "3 Link Avenue, Abuja" in values               # ordinary office kept


def test_ac6_never_stores_background_research_notes():
    # Spec: F-026c-registrar-research-import.md | AC-6
    plan = _build()
    blob = str(_field_values(_ops(plan, CreateFieldOp)))
    assert "never-a-page-value" not in blob   # internal_research_notes
    assert "example.invalid" not in blob      # evidence_sources
    assert "background only" not in blob      # latest_operating_evidence


def test_ac7_head_office_from_the_file_gets_the_confirm_suffix():
    # Spec: F-026c-registrar-research-import.md | AC-7
    plan = _build()
    head = [op for op in _fields(plan, 1)
            if op.field_value == "1 Alpha Way, Lagos"]
    assert len(head) == 1
    assert head[0].field_type == "address"
    assert head[0].label == "Head office (please confirm)"
    # A-4: the head office sorts base+10, base = max(existing sort_order) = 10
    assert head[0].sort_order == 20


def test_field_sort_orders_step_by_10_after_existing_fields():
    # Spec: F-026c-registrar-research-import.md | AC-7
    """A-4: every new field is numbered after K's existing active fields —
    base = max(existing sort_order), head office = base+10, the rest in steps
    of 10 (the existing max sort_order on #1 is 10, and the moved field of
    the duplicate only sorts 1)."""
    plan = _build()
    alpha = _fields(plan, 1)
    head = [op for op in alpha if op.field_value == "1 Alpha Way, Lagos"][0]
    rest = [op.sort_order for op in alpha if op is not head]
    assert rest == sorted(rest)
    assert all(order % 10 == 0 for order in rest)
    assert min(rest) == 30                       # base 10 -> head 20 -> 30

    newbies = _fields(plan, ("new", "newbies"))
    head2 = [op for op in newbies
             if op.field_value == "5 Newbie Close, Ikeja, Lagos"][0]
    rest2 = [op.sort_order for op in newbies if op is not head2]
    assert min(rest2) == 20                      # base 0 -> head 10 -> 20


def test_ac10_weak_mappings_are_held_back_and_get_no_link_change():
    # Spec: F-026c-registrar-research-import.md | AC-10
    plan = _build()
    assert [h["ticker"] for h in plan.held_back] == ["WEAKCO", "UNVCO"]
    # the only change to WEAKCO's link is the §4.1 merge re-point
    assert [op.link_id for op in _ops(plan, RepointLinkOp)] == [202]
    assert not any(
        isinstance(op, (CreateLinkOp, EnsurePrimaryLinkOp))
        and op.company_id == 102
        for op in plan.ops
    )
    # merge re-points the legacy FK too (§4.1.2); the firm mapping of the
    # brand new registrar is the only other companies.registrar_id change
    company_ops = _ops(plan, UpdateCompanyOp)
    assert [(op.company_id, op.changes) for op in company_ops] == [
        (102, {"registrar_id": 1}),
        (103, {"registrar_id": ("new", "newbies")}),
    ]


def test_ac11_unmatched_tickers_create_no_company_and_are_reported():
    # Spec: F-026c-registrar-research-import.md | AC-11
    plan = _build()
    assert [u["ticker"] for u in plan.unmatched] == ["GHOST", None]
    assert plan.counts["companies_registrar_changed"] == 2
    assert not any("GHOST" in line for line in plan.lines)
    assert any("GHOST" in line for line in plan.report_lines)


def test_without_contact_record_rows_are_reported():
    # Spec: F-026c-registrar-research-import.md | AC-11
    plan = _build()
    assert [u["ticker"] for u in plan.without_contact_record] == ["NOREC"]


def test_firm_mapping_keeps_one_active_primary_and_drops_the_others():
    # Spec: F-026c-registrar-research-import.md | AC-10
    """ALPHA is firm on canonical #1: its other active primary (link 203,
    registrar #2, which is not in the resolution table) is soft-deleted,
    and the already-correct link 201 is left alone."""
    plan = _build()
    assert [op.link_id for op in _ops(plan, SoftDeleteLinkOp)] == [203]
    assert not any(
        isinstance(op, (CreateLinkOp, EnsurePrimaryLinkOp))
        and op.company_id == 101
        for op in plan.ops
    )


def test_firm_mapping_for_a_new_registrar_creates_the_link():
    # Spec: F-026c-registrar-research-import.md | AC-10
    plan = _build()
    created = _ops(plan, CreateLinkOp)
    assert [(op.company_id, op.registrar_key) for op in created] == [
        (103, ("new", "newbies")),
    ]


# ─── merge / legacy / labels in the plan (§4.1–§4.3) ───────────────────────────

def test_merge_plan_for_the_duplicate():
    # Spec: F-026c-registrar-research-import.md | AC-4
    plan = _build()
    assert isinstance(plan.ops[0], CreateRegistrarOp)      # new registrars first
    renames = _ops(plan, RenameRegistrarOp)
    assert [(op.registrar_id, op.new_name) for op in renames] == [
        (1, "Alpha Registrars Limited"),
    ]
    assert [(op.link_id, op.to_registrar_id)
            for op in _ops(plan, RepointLinkOp)] == [(202, 1)]
    assert [(op.requirement_id, op.to_registrar_id)
            for op in _ops(plan, RepointRequirementOp)] == [(301, 1)]
    assert [(op.field_id, op.to_registrar_id)
            for op in _ops(plan, MoveFieldOp)] == [(102, 1)]
    assert [op.registrar_id for op in _ops(plan, SoftDeleteRegistrarOp)] == [3]

    rating_updates = [op for op in _ops(plan, UpdateRegistrarOp)
                      if "response_rating" in op.changes]
    assert len(rating_updates) == 1
    assert rating_updates[0].registrar_key == 1
    assert rating_updates[0].changes["response_rating"] == 4
    assert rating_updates[0].changes["notes"] == "[merged from #3] hand notes"


def test_legacy_columns_become_entered_manually_fields():
    # Spec: F-026c-registrar-research-import.md | AC-4
    plan = _build()
    manual = [op for op in _fields(plan, 1) if op.label == "Entered manually"]
    assert {(op.field_type, op.field_value) for op in manual} == {
        ("phone", "01 555 0100"),              # non-NULL legacy column on #1
        ("email", "old@alpha.example"),         # legacy column of duplicate #3
    }


def test_legacy_columns_are_filled_only_when_null():
    # Spec: F-026c-registrar-research-import.md | AC-5
    plan = _build()
    legacy_cols = {"email", "phone", "address", "website"}
    fills = {op.registrar_key: op.changes
             for op in _ops(plan, UpdateRegistrarOp)
             if set(op.changes) & legacy_cols}
    # #1: phone is hand-entered (never overwritten), website is not safe_to_link
    assert fills[1] == {
        "email": "desk@alpha.example",
        "address": "1 Alpha Way, Lagos",
    }
    # the brand new registrar gets every NULL column filled, website included
    assert fills[("new", "newbies")] == {
        "email": "hello@newbies.example",
        "phone": "+2342000000001",
        "address": "5 Newbie Close, Ikeja, Lagos",
        "website": "https://newbies.example",
    }
    # registrar #2 is not in the file at all: untouched
    assert 2 not in fills


def test_plan_counts_and_formatting():
    # Spec: F-026c-registrar-research-import.md | AC-1
    plan = _build()
    assert plan.counts["registrars_created"] == 1
    assert plan.counts["registrars_merged"] == 1
    assert plan.counts["registrars_soft_deleted"] == 1
    assert plan.counts["registrars_renamed"] == 1
    assert plan.counts["links_created"] == 1
    assert plan.counts["links_soft_deleted"] == 1
    assert plan.counts["links_reactivated"] == 0
    assert plan.report_counts == {
        "held_back": 2, "unmatched": 2, "without_contact_record": 1,
    }
    block = "\n".join(plan.counts_block())
    assert "registrars: created=1 merged=1 soft-deleted=1 renamed=1" in block
    assert "held back (weak)=2" in block


# ─── AC-14: §3 resolution checks ────────────────────────────────────────────────

def test_ac14_canonical_id_whose_name_does_not_contain_the_slug_word():
    # Spec: F-026c-registrar-research-import.md | AC-14
    table = _resolution_table()
    table["alpha"] = ResolutionEntry(
        slug="alpha", canonical=2, duplicates=(), final_name=None)
    with pytest.raises(ResolutionError) as exc:
        build_plan(_research(), _snapshot(), table)
    assert "alpha" in str(exc.value)


def test_ac14_missing_id_and_soft_deleted_id_abort_the_plan():
    # Spec: F-026c-registrar-research-import.md | AC-14
    table = _resolution_table()
    table["alpha"] = ResolutionEntry(
        slug="alpha", canonical=999, duplicates=(), final_name=None)
    with pytest.raises(ResolutionError):
        build_plan(_research(), _snapshot(), table)

    snapshot = _snapshot()
    snapshot.registrars[1].deleted_at = snapshot.registrars[1].deleted_at or True
    with pytest.raises(ResolutionError):
        build_plan(_research(), snapshot, _resolution_table())


def test_ac14_duplicate_id_is_verified_too():
    # Spec: F-026c-registrar-research-import.md | AC-14
    table = _resolution_table()
    table["alpha"] = ResolutionEntry(
        slug="alpha", canonical=1, duplicates=(2,), final_name=None)  # Beta
    with pytest.raises(ResolutionError):
        build_plan(_research(), _snapshot(), table)


def test_ac14_file_slug_missing_from_the_table_aborts():
    # Spec: F-026c-registrar-research-import.md | AC-14
    table = _resolution_table()
    del table["newbies"]
    with pytest.raises(ResolutionError):
        build_plan(_research(), _snapshot(), table)
    with pytest.raises(ResolutionError):
        build_plan(_research(), _snapshot(), {"nope": ResolutionEntry(
            slug="nope", canonical=None, duplicates=(), final_name="X")})


def test_ac14_confirm_db_must_equal_the_connected_database():
    # Spec: F-026c-registrar-research-import.md | AC-14
    check_confirm_db("epm_test", "epm_test")            # equal: no exception
    with pytest.raises(ConfirmDatabaseError):
        check_confirm_db("estate", "epm_test")          # different database
    with pytest.raises(ConfirmDatabaseError):
        check_confirm_db(None, "epm_test")               # --confirm-db missing


def test_ac1_refuses_to_run_without_database_url(monkeypatch):
    # Spec: F-026c-registrar-research-import.md | AC-1
    """A-7: --undo-out is now part of a legal --apply invocation, so the flag
    is given here too and the refusal is still about DATABASE_URL."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    rc = asyncio.run(amain(["--apply", "--undo-out", "-", "--confirm-db", "epm_test"]))
    assert rc != 0


def test_apply_without_confirm_db_refuses_before_touching_anything():
    # Spec: F-026c-registrar-research-import.md | AC-14
    """A-7: --undo-out is given so the check that fires is the missing
    --confirm-db (AC-14), not the new A-7 flag rule."""
    rc = asyncio.run(amain(["--apply", "--undo-out", "-"]))
    assert rc != 0


# ─── A-1: a merge never leaves a company with fewer active links ──────────────

def test_a1_merge_reactivates_the_canonicals_soft_deleted_row():
    # Spec: F-026c-registrar-research-import.md | AC-8
    """A-1 (audit #4): K's row for the company is soft-deleted and D's row is
    active => the plan reactivates K's row keeping D's role and soft-deletes
    D's row, so the company keeps exactly one active link to the canonical."""
    plan = build_plan(_research(), _snapshot_ghost(), _resolution_table())
    reactivations = {op.link_id: op for op in _ops(plan, EnsurePrimaryLinkOp)}
    assert sorted(reactivations) == [205, 207]
    # the reactivated row keeps D's role
    assert reactivations[205].role == "primary"        # D link 204 is a primary
    assert reactivations[207].role == "co_registrar"    # D link 206 is a co_registrar
    # D's rows are soft-deleted exactly once each (nothing else touches them)
    assert sorted(op.link_id for op in _ops(plan, SoftDeleteLinkOp)) == [203, 204, 206]

    # after the plan has run both companies still have one active link, to #1
    state = imp.apply_ops_to_snapshot(_snapshot_ghost(), plan.ops)
    for company_id, link_id, role in ((105, 205, "primary"),
                                      (106, 207, "co_registrar")):
        active = [l for l in state.links
                  if l.company_id == company_id and not l.deleted_at]
        assert [(l.id, l.registrar_id, l.role) for l in active] == [
            (link_id, 1, role)]


# ─── A-2: a firm reactivation sets role='primary' ─────────────────────────────

def test_a2_firm_reactivation_sets_role_primary():
    # Spec: F-026c-registrar-research-import.md | AC-8
    """A-2 (audit #5): reactivating the (company, K) row for a firm mapping
    sets deleted_at=NULL AND role='primary' in the same operation."""
    snapshot = _snapshot()
    snapshot.links[0].deleted_at = True      # link 201: #1's row for ALPHA
    plan = build_plan(_research(), snapshot, _resolution_table())
    reactivations = [op for op in _ops(plan, EnsurePrimaryLinkOp)
                     if op.company_id == 101]
    assert len(reactivations) == 1
    assert reactivations[0].link_id == 201
    assert reactivations[0].role == "primary"
    # the reactivation is the only other link change for company 101:
    # the foreign primary (link 203) is retired, no row is created
    assert [op.link_id for op in _ops(plan, SoftDeleteLinkOp)] == [203]
    assert not any(isinstance(op, CreateLinkOp) and op.company_id == 101
                    for op in plan.ops)


class _RecordingSession:
    """The smallest session ``apply_plan`` accepts: every statement is kept,
    so a test can read back the UPDATE the database would have received —
    no connection is ever made (A-2 at the SQL layer)."""

    def __init__(self):
        self.statements = []

    async def execute(self, statement, *args, **kwargs):
        self.statements.append(statement)
        if statement.__class__.__name__ == "TextClause":
            return _ScalarResult()             # current_database()
        return _FakeSelectResult()             # _previous_values

    async def flush(self):
        self.statements.append("flush")


class _ScalarResult:
    def scalar_one(self):
        return "epm_test"


class _FakeSelectResult:
    def one(self):
        # _mapping answers every column name, so _previous_values() can ask
        # for updated_at without the fake having to know the table
        return type("Row", (), {"_mapping": defaultdict(lambda: None)})()

    def first(self):
        return None


def test_a2_apply_writes_deleted_at_and_role_in_one_statement():
    # Spec: F-026c-registrar-research-import.md | AC-8
    """A-2: the reactivation statement carries both columns — deleted_at=NULL
    and role='primary' — and the undo record records both as previous values."""
    session = _RecordingSession()
    plan = imp.Plan()
    plan.ops.append(EnsurePrimaryLinkOp(company_id=101, registrar_key=1,
                                        link_id=201, role="primary"))
    record = asyncio.run(imp.apply_plan(session, plan))

    updates = [stmt for stmt in session.statements
               if stmt.__class__.__name__ == "Update"]
    assert len(updates) == 1
    params = updates[0].compile().params
    assert params["role"] == "primary"
    assert "deleted_at" in params            # both columns, one statement
    # the undo record knows both columns were written
    assert {"deleted_at", "role"} <= set(record.entries[0]["previous"])


# ─── A-3: legacy fills keep the plan idempotent ───────────────────────────────

def _research_with_hidden_primary_email():
    """The same fixture with alpha's primary email hidden from the page
    (show_on_page: false): filling the NULL legacy column with it would store a
    value that has no visible field, and the NEXT run would then copy that
    column back as an "Entered manually" field — audit #6."""
    research = _research()
    for email in research.registrars[0]["emails"]:
        if email["address"] == "desk@alpha.example":
            email["show_on_page"] = False
    return research


def test_a3_a_legacy_column_is_filled_only_with_a_visible_value():
    # Spec: F-026c-registrar-research-import.md | AC-12
    """A-3 clause 1: the file may fill a NULL legacy column only with a value
    that is also stored (or already present) as a visible field on K."""
    plan = build_plan(_research_with_hidden_primary_email(),
                      _snapshot(), _resolution_table())
    fills = {op.registrar_key: set(op.changes)
             for op in _ops(plan, UpdateRegistrarOp)
             if set(op.changes) & {"email", "phone", "address", "website"}}
    # the primary email is not visible on the page => the column stays NULL
    assert "email" not in fills.get(1, set())
    # the head office address is visible => the NULL address column may take it
    assert "address" in fills.get(1, set())


def test_a3_second_plan_on_the_post_apply_state_plans_zero_ops():
    # Spec: F-026c-registrar-research-import.md | AC-12
    """A-3/audit #6: build the plan, apply it to the snapshot (the same working
    copy the planner updates, A-6), build the plan again on the post-apply
    state and get an empty plan."""
    research = _research_with_hidden_primary_email()
    first = build_plan(research, _snapshot(), _resolution_table())
    state = imp.apply_ops_to_snapshot(_snapshot(), first.ops)
    second = build_plan(research, state, _resolution_table())
    assert second.ops == [], second.lines
    assert all(value == 0 for value in second.counts.values()), second.counts


# ─── A-4: sort_order is numbered after K's existing fields ────────────────────

def test_a4_new_fields_are_numbered_after_the_existing_ones():
    # Spec: F-026c-registrar-research-import.md | AC-7
    """A-4 (audit #7): base = max(existing active sort_order), head office =
    base+10, then the rest in steps of 10."""
    plan = _build()
    alpha = {op.field_value: op.sort_order for op in _fields(plan, 1)}
    assert alpha["1 Alpha Way, Lagos"] == 20            # base 10 + 10
    rest = sorted(order for value, order in alpha.items()
                  if value != "1 Alpha Way, Lagos")
    assert rest[0] == 30
    assert rest == list(range(30, 30 + 10 * len(rest), 10))

    newbies = {op.field_value: op.sort_order
               for op in _fields(plan, ("new", "newbies"))}
    assert newbies["5 Newbie Close, Ikeja, Lagos"] == 10   # base 0 + 10
    rest2 = sorted(order for value, order in newbies.items()
                   if value != "5 Newbie Close, Ikeja, Lagos")
    assert rest2[0] == 20
    assert rest2 == list(range(20, 20 + 10 * len(rest2), 10))


# ─── A-5: a trailing slash does not duplicate a website/portal ────────────────

def test_a5_a_trailing_slash_does_not_create_a_second_field():
    # Spec: F-026c-registrar-research-import.md | AC-5
    """A-5 (audit #8): for websites and portals one trailing "/" is stripped
    before the values are compared."""
    snapshot = _snapshot()
    snapshot.fields.extend([
        FieldRow(id=103, registrar_id=1, field_type="website",
                 field_value="https://alpha.example/", label="web",
                 sort_order=20, deleted_at=None),
        FieldRow(id=104, registrar_id=1, field_type="other",
                 field_value="https://portal.alpha.example/", label="portal",
                 sort_order=30, deleted_at=None),
    ])
    plan = build_plan(_research(), snapshot, _resolution_table())
    created = _field_values(_fields(plan, 1))
    # the file carries both URLs without the slash: no second copy of either
    assert "https://alpha.example" not in created
    assert "https://portal.alpha.example" not in created
    assert "https://portal.alpha.example/" not in created
    # and the normalisation itself is the rule the amendment asks for
    assert normalise("https://alpha.example/") == normalise("https://alpha.example")
    assert normalise("https://alpha.example/", "website") == normalise("https://alpha.example")
    assert normalise("https://portal.alpha.example/") == normalise("https://portal.alpha.example")


# ─── A-6 / AC-16: plan integrity ──────────────────────────────────────────────

def _touches(op):
    """(table, row_id, column) of every column of an EXISTING row the op
    changes. Insert operations are left out: they cannot collide with a
    second op, and a ("new", slug) key names a row that does not exist yet."""
    if isinstance(op, (CreateRegistrarOp, CreateFieldOp, CreateLinkOp)):
        return []
    if isinstance(op, RenameRegistrarOp):
        return [("registrars", op.registrar_id, "name")]
    if isinstance(op, UpdateRegistrarOp):
        if not isinstance(op.registrar_key, int):
            return []                            # writes a row the apply created
        return [("registrars", op.registrar_key, col) for col in op.changes]
    if isinstance(op, SoftDeleteRegistrarOp):
        return [("registrars", op.registrar_id, "deleted_at")]
    if isinstance(op, MoveFieldOp):
        return [("registrar_contact_fields", op.field_id, "registrar_id")]
    if isinstance(op, SoftDeleteLinkOp):
        return [("company_registrars", op.link_id, "deleted_at")]
    if isinstance(op, EnsurePrimaryLinkOp):
        if op.link_id is None:
            return []                            # resolved at apply time
        return [("company_registrars", op.link_id, "deleted_at"),
                ("company_registrars", op.link_id, "role")]
    if isinstance(op, RepointLinkOp):
        return [("company_registrars", op.link_id, "registrar_id")]
    if isinstance(op, RepointRequirementOp):
        return [("registrar_requirements", op.requirement_id, "registrar_id")]
    if isinstance(op, UpdateCompanyOp):
        if not isinstance(op.company_id, int):
            return []
        return [("companies", op.company_id, col) for col in op.changes]
    raise AssertionError(f"unhandled plan operation: {op!r}")


def _merge_firm_rows(op):
    """(table, row_id) of every EXISTING row the MERGE step or the FIRM step
    writes — the row-level (A-8) twin of the column-level :func:`_touches`
    check above.

    Inserts are left out: they have no id yet and cannot collide. So are the
    create / rename / contacts steps: A-8 scopes "one op per row" to the two
    steps auditor pass 2 found writing one row twice (#1/#2 across merge and
    firm, #4 across two merges). A ``UpdateRegistrarOp`` that only carries
    legacy columns is the contacts step's "fill NULL legacy columns", not a
    merged value."""
    if isinstance(op, (CreateRegistrarOp, CreateFieldOp, CreateLinkOp,
                       RenameRegistrarOp)):
        return []
    if isinstance(op, UpdateRegistrarOp) and \
            set(op.changes) <= set(imp.LEGACY_COLUMNS):
        return []
    return [(table, row_id) for table, row_id, _column in _touches(op)]


@pytest.mark.parametrize("snapshot_factory", [_snapshot, _snapshot_ghost])
def test_ac16_no_row_or_column_is_changed_twice_and_counts_are_distinct(
        snapshot_factory):
    # Spec: F-026c-registrar-research-import.md | AC-16
    """A-6: no row/column is changed by two ops, and every count equals the
    number of distinct rows it claims to cover."""
    plan = build_plan(_research(), snapshot_factory(), _resolution_table())
    seen = set()
    for op in plan.ops:
        for touch in _touches(op):
            assert touch not in seen, (
                f"{touch} changed twice: {plan.lines}")
            seen.add(touch)

    assert plan.counts["registrars_soft_deleted"] == len(
        {op.registrar_id for op in _ops(plan, SoftDeleteRegistrarOp)})
    assert plan.counts["fields_moved"] == len(
        {op.field_id for op in _ops(plan, MoveFieldOp)})
    assert plan.counts["fields_added"] == len(_ops(plan, CreateFieldOp))
    assert plan.counts["links_created"] == len(_ops(plan, CreateLinkOp))
    assert plan.counts["links_repointed"] == len(
        {op.link_id for op in _ops(plan, RepointLinkOp)})
    assert plan.counts["links_reactivated"] == len(
        {op.link_id for op in _ops(plan, EnsurePrimaryLinkOp)
         if op.link_id is not None})
    assert plan.counts["links_soft_deleted"] == len(
        {op.link_id for op in _ops(plan, SoftDeleteLinkOp)})
    assert plan.counts["requirements_repointed"] == len(
        {op.requirement_id for op in _ops(plan, RepointRequirementOp)})
    assert plan.counts["companies_registrar_changed"] == len(
        {op.company_id for op in _ops(plan, UpdateCompanyOp)})


def test_a6_merged_company_that_is_also_firm_mapped_gets_one_consistent_before():
    # Spec: F-026c-registrar-research-import.md | AC-16
    """A-6/audit #1: company 105 is merged (link of duplicate #3) AND firmly
    mapped to canonical #1 by the file. Its companies.registrar_id must be
    changed exactly once — the merge — and the firm mapping must add no second
    change, no second soft-delete and no stale "before" value."""
    snapshot = _snapshot_ghost()
    plan = build_plan(_research(), snapshot, _resolution_table())

    company_ops = [op for op in _ops(plan, UpdateCompanyOp)
                   if op.company_id == 105]
    assert [op.changes for op in company_ops] == [{"registrar_id": 1}]
    # the "before" value the plan line shows is the value in the snapshot
    assert [line for line in plan.lines
            if line.startswith("company #105:")] == [
        "company #105: registrar_id #3 -> #1"]
    # every link op on company 105 belongs to the merge, once
    assert sorted(op.link_id for op in _ops(plan, SoftDeleteLinkOp)
                  if op.link_id in (204, 205)) == [204]
    assert [op.link_id for op in _ops(plan, EnsurePrimaryLinkOp)
            if op.link_id in (204, 205)] == [205]
    assert not any(isinstance(op, CreateLinkOp) and op.company_id == 105
                    for op in plan.ops)


# ─── A-8 / A-9 / AC-16 round 2: the production shape of preview #2 ────────────

def _research_round2():
    """The fixture file plus three FIRM clients under ``newbies`` — K2 in the
    round-2 table — so the shape production preview #2 showed is in the data."""
    research = _research()
    newbies = next(r for r in research.registrars if r["slug"] == "newbies")
    newbies["clients"] = [
        {"company": "Firm Mover Plc", "ticker": "FMO",
         "mapping_confidence": "High", "mapping_flag": "OK"},
        {"company": "Soft Deleted Row Co Plc", "ticker": "SDCO",
         "mapping_confidence": "Medium", "mapping_flag": "OK"},
        {"company": "Co Registrar Plc", "ticker": "COREG",
         "mapping_confidence": "High", "mapping_flag": "SINGLE-SOURCE"},
    ] + newbies["clients"]
    return research


def _resolution_table_round2():
    """The round-2 table: alpha gains a SECOND duplicate (#4) and newbies is an
    existing canonical (#2), so a company can sit on a duplicate of one
    canonical (K1 = #1) while the file firmly maps it to another (K2 = #2)."""
    return {
        "alpha": ResolutionEntry(
            slug="alpha", canonical=1, duplicates=(3, 4),
            final_name="Alpha Registrars Limited",
        ),
        "newbies": ResolutionEntry(
            slug="newbies", canonical=2, duplicates=(), final_name=None,
        ),
    }


def _snapshot_round2():
    """``_snapshot()`` plus the shape production preview #2 exposed (AC-16):

    * registrar #4 — a second duplicate of canonical #1, with notes AND a
      rating of its own: both duplicates merge their values into #1, and those
      values have to land in ONE op (audit-2 #4);
    * ``FMO`` (company 107, active duplicate link) and ``SDCO`` (company 108,
      K1's own row already soft-deleted) sit on duplicate #3 of K1 = #1 while
      the file firmly maps them to K2 = #2: neither may be re-pointed toward K1
      by the merge, each gets exactly one ``registrar_id`` op — straight from
      the snapshot value to K2 — and each link row is handled once (audit-2
      #1/#2);
    * ``COREG`` (company 109) is firmly mapped to #2, whose own active row for
      it is a ``co_registrar``: A-9 holds the whole company back (AC-18).
    """
    snapshot = _snapshot()
    # §3 name check: the canonical of the slug "newbies" must contain it
    snapshot.registrars[2].name = "Newbies Registrars Limited"
    snapshot.registrars[4] = RegistrarRow(
        id=4, name="Alpha Ancient Registrars Limited",
        email=None, phone=None, address=None, website=None,
        response_rating=3, notes="second duplicate notes",
        status="active", jurisdiction="nigeria", deleted_at=None,
    )
    snapshot.companies.extend([
        CompanyRow(id=107, ticker="FMO", name="Firm Mover Plc",
                   registrar_id=3, deleted_at=None),
        CompanyRow(id=108, ticker="SDCO", name="Soft Deleted Row Co Plc",
                   registrar_id=3, deleted_at=None),
        CompanyRow(id=109, ticker="COREG", name="Co Registrar Plc",
                   registrar_id=1, deleted_at=None),
    ])
    snapshot.links.extend([
        # 107: the duplicate's link is ACTIVE, K1 has no row for it
        LinkRow(id=208, company_id=107, registrar_id=3, role="primary",
                deleted_at=None),
        # 108: the duplicate's link is ACTIVE and K1's own row is soft-deleted
        LinkRow(id=209, company_id=108, registrar_id=3, role="primary",
                deleted_at=None),
        LinkRow(id=210, company_id=108, registrar_id=1, role="primary",
                deleted_at=True),
        # 109: K2's own row for it is an active co_registrar (A-9)
        LinkRow(id=211, company_id=109, registrar_id=1, role="primary",
                deleted_at=None),
        LinkRow(id=212, company_id=109, registrar_id=2, role="co_registrar",
                deleted_at=None),
    ])
    return snapshot


def _round2_plan():
    return build_plan(_research_round2(), _snapshot_round2(),
                      _resolution_table_round2())


def test_ac16_round2_no_row_is_changed_twice_by_the_merge_or_firm_step():
    # Spec: F-026c-registrar-research-import.md | AC-16
    """Row-level A-8 on the production-shaped snapshot: no (table, id) appears
    in two ops of the merge or firm steps, and every count equals its number of
    distinct rows."""
    plan = _round2_plan()
    seen = set()
    for op in plan.ops:
        for touch in _merge_firm_rows(op):
            assert touch not in seen, (
                f"{touch} changed by two ops: {plan.lines}")
            seen.add(touch)

    assert plan.counts["registrars_created"] == len(
        {op.key for op in _ops(plan, CreateRegistrarOp)})
    assert plan.counts["registrars_soft_deleted"] == len(
        {op.registrar_id for op in _ops(plan, SoftDeleteRegistrarOp)})
    assert plan.counts["registrars_renamed"] == len(
        {op.registrar_id for op in _ops(plan, RenameRegistrarOp)})
    assert plan.counts["fields_moved"] == len(
        {op.field_id for op in _ops(plan, MoveFieldOp)})
    assert plan.counts["fields_added"] == len(_ops(plan, CreateFieldOp))
    assert plan.counts["links_created"] == len(_ops(plan, CreateLinkOp))
    assert plan.counts["links_repointed"] == len(
        {op.link_id for op in _ops(plan, RepointLinkOp)})
    assert plan.counts["links_reactivated"] == len(
        {op.link_id for op in _ops(plan, EnsurePrimaryLinkOp)
         if op.link_id is not None})
    assert plan.counts["links_soft_deleted"] == len(
        {op.link_id for op in _ops(plan, SoftDeleteLinkOp)})
    assert plan.counts["requirements_repointed"] == len(
        {op.requirement_id for op in _ops(plan, RepointRequirementOp)})
    assert plan.counts["companies_registrar_changed"] == len(
        {op.company_id for op in _ops(plan, UpdateCompanyOp)})


def test_a8_firm_mapped_company_on_a_duplicate_gets_one_op_straight_to_k2():
    # Spec: F-026c-registrar-research-import.md | AC-16
    """A-8: FMO and SDCO sit on duplicate #3 of K1 = #1 and are firmly mapped
    to K2 = #2. The merge gives them no re-point toward K1: one registrar_id
    op each, from the snapshot value straight to K2, and their duplicate links
    are handled once — by the firm step (a link row that ends soft-deleted is
    not re-pointed or reactivated first)."""
    plan = _round2_plan()
    for company_id in (107, 108):
        company_ops = [op for op in _ops(plan, UpdateCompanyOp)
                        if op.company_id == company_id]
        assert [op.changes for op in company_ops] == [{"registrar_id": 2}], (
            plan.lines)
        assert [line for line in plan.lines
                if line.startswith(f"company #{company_id}: registrar_id ")] == [
            f"company #{company_id}: registrar_id 3 -> 2"]

    # the duplicate's links: retired once each by the firm step, never
    # re-pointed toward K1 first, and K1's soft-deleted row 210 is never
    # reactivated
    assert sorted(op.link_id for op in _ops(plan, SoftDeleteLinkOp)
                  if op.link_id in (208, 209, 210)) == [208, 209]
    assert not any(op.link_id in (208, 209, 210)
                   for op in _ops(plan, RepointLinkOp))
    assert not any(op.link_id == 210 for op in _ops(plan, EnsurePrimaryLinkOp))

    # after the plan each of them has exactly one active primary, on K2
    state = imp.apply_ops_to_snapshot(_snapshot_round2(), plan.ops)
    for company_id in (107, 108):
        active = [link for link in state.links
                  if link.company_id == company_id and not link.deleted_at]
        assert [(link.registrar_id, link.role) for link in active] == [
            (2, "primary")], plan.lines
        company = next(c for c in state.companies if c.id == company_id)
        assert company.registrar_id == 2


def test_a8_two_duplicates_merge_their_values_into_one_registrar_op():
    # Spec: F-026c-registrar-research-import.md | AC-16
    """A-8: the values both duplicates merge into canonical #1 — notes and the
    response rating — land in a single UpdateRegistrarOp, holding the final
    value of each column (audit-2 #4: notes changed by two ops)."""
    plan = _round2_plan()
    merged = [op for op in _ops(plan, UpdateRegistrarOp)
              if op.registrar_key == 1
              and set(op.changes) & {"notes", "response_rating"}]
    assert len(merged) == 1, plan.lines
    assert merged[0].changes == {
        # #3's rating: K was NULL, so #4's rating of 3 is NOT copied over it
        "response_rating": 4,
        "notes": ("[merged from #3] hand notes\n"
                  "[merged from #4] second duplicate notes"),
    }
    # both duplicates are still merged and soft-deleted exactly once each
    assert [op.registrar_id for op in _ops(plan, SoftDeleteRegistrarOp)] == [3, 4]
    assert plan.counts["registrars_merged"] == 2


def test_ac18_co_registrar_at_the_firm_target_holds_the_company_back():
    # Spec: F-026c-registrar-research-import.md | AC-18
    """A-9: COREG is firmly mapped to #2, whose active row for it is a
    co_registrar. Nothing at all is changed for the company — no link op, no
    registrar_id op — and it is listed for the Product Owner as
    ``held back (co_registrar at target)``."""
    plan = _round2_plan()
    assert not any(
        isinstance(op, UpdateCompanyOp) and op.company_id == 109
        for op in plan.ops), plan.lines
    assert not any(
        isinstance(op, (SoftDeleteLinkOp, EnsurePrimaryLinkOp, RepointLinkOp))
        and op.link_id in (211, 212)
        for op in plan.ops), plan.lines
    assert not any(isinstance(op, CreateLinkOp) and op.company_id == 109
                   for op in plan.ops), plan.lines

    assert any(
        line.startswith("held back (co_registrar at target): COREG")
        for line in plan.report_lines), plan.report_lines
    # the weak list keeps exactly the weak mappings (A-9 does not fold them in)
    assert [h["ticker"] for h in plan.held_back] == ["WEAKCO", "UNVCO"]

    # the snapshot rows of COREG survive untouched, one active primary included
    state = imp.apply_ops_to_snapshot(_snapshot_round2(), plan.ops)
    active = [link for link in state.links
              if link.company_id == 109 and not link.deleted_at]
    assert [(link.id, link.registrar_id, link.role) for link in active] == [
        (211, 1, "primary"), (212, 2, "co_registrar")]
    company = next(c for c in state.companies if c.id == 109)
    assert company.registrar_id == 1


# ─── A-7 / AC-17: the undo record is written before COMMIT ────────────────────

class _FakeResult:
    def scalar_one(self):
        return "epm_test"


class _FakeTransaction:
    """Records the order of begin / commit / rollback; never swallows errors."""

    def __init__(self, events):
        self.events = events

    async def __aenter__(self):
        self.events.append("begin")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.events.append("rollback" if exc_type else "commit")
        return False


class _FakeSession:
    def __init__(self, events):
        self.events = events

    def begin(self):
        return _FakeTransaction(self.events)

    async def close(self):
        self.events.append("close")

    async def execute(self, statement, *args, **kwargs):
        return _FakeResult()          # current_database() -> "epm_test"


class _FakeConnection:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeEngine:
    def __init__(self, events):
        self.events = events

    def connect(self):
        self.events.append("connect")
        return _FakeConnection()

    async def dispose(self):
        self.events.append("dispose")


def _fake_cli(monkeypatch, events):
    """cli() wired to a fake engine and a fake session, with the snapshot,
    the plan and the undo record faked too — the transaction ORDER of an
    --apply is then observable without any database (AC-17)."""
    monkeypatch.setattr(imp, "create_async_engine",
                        lambda *args, **kwargs: _FakeEngine(events))
    monkeypatch.setattr(imp, "AsyncSession",
                        lambda **kwargs: _FakeSession(events))
    monkeypatch.setattr(imp, "RESOLUTION_TABLE", _resolution_table())

    async def fake_load_snapshot(session):
        events.append("load_snapshot")
        return _snapshot()

    async def fake_apply_plan(session, plan):
        events.append("apply_plan")
        return UndoRecord(
            database="epm_test", applied_at="2026-11-28T00:00:00+00:00",
            counts=dict(plan.counts),
            entries=[{"table": "registrars", "id": 1,
                      "previous": {"name": "old name"}}],
        )

    monkeypatch.setattr(imp, "load_snapshot", fake_load_snapshot)
    monkeypatch.setattr(imp, "apply_plan", fake_apply_plan)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://epm:secret@example.test/epm_test",
    )
    return imp


def test_ac17_apply_without_undo_out_exits_non_zero(monkeypatch, capsys):
    # Spec: F-026c-registrar-research-import.md | AC-17
    """A-7: --apply refuses to run without --undo-out <path|->, before it
    even looks at DATABASE_URL."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    rc = asyncio.run(amain(["--apply", "--confirm-db", "epm_test"]))
    assert rc != 0
    assert "--undo-out" in capsys.readouterr().err


def test_ac17_the_undo_record_is_written_before_the_commit(
        monkeypatch, tmp_path, capsys):
    # Spec: F-026c-registrar-research-import.md | AC-17
    """A-7: the undo writer runs inside the transaction, before COMMIT."""
    events = []
    mod = _fake_cli(monkeypatch, events)
    real_write = mod._write_undo

    def spy(record, undo_out):
        events.append("write_undo")
        return real_write(record, undo_out)

    monkeypatch.setattr(mod, "_write_undo", spy)
    undo_path = tmp_path / "undo.json"
    rc = asyncio.run(mod.cli(
        ["--apply", "--confirm-db", "epm_test", "--undo-out", str(undo_path)],
        research_text=FIXTURE.read_text(encoding="utf-8"),
    ))
    assert rc == 0, capsys.readouterr().err
    assert "apply_plan" in events and "write_undo" in events and "commit" in events
    assert events.index("apply_plan") < events.index("write_undo")
    assert events.index("write_undo") < events.index("commit")
    assert "rollback" not in events

    payload = json.loads(undo_path.read_text(encoding="utf-8"))
    assert payload["feature"] == "F-026c"
    assert payload["database"] == "epm_test"
    assert payload["entries"] == [
        {"table": "registrars", "id": 1, "previous": {"name": "old name"}}]


def test_ac17_a_failing_undo_writer_rolls_the_apply_back(
        monkeypatch, tmp_path, capsys):
    # Spec: F-026c-registrar-research-import.md | AC-17
    """A-7: if writing the undo record fails, the transaction rolls back —
    nothing is committed and the CLI exits non-zero."""
    events = []
    mod = _fake_cli(monkeypatch, events)
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("x", encoding="utf-8")     # mkdir() over this fails
    undo_path = blocker / "undo.json"

    rc = asyncio.run(mod.cli(
        ["--apply", "--confirm-db", "epm_test", "--undo-out", str(undo_path)],
        research_text=FIXTURE.read_text(encoding="utf-8"),
    ))
    assert rc != 0
    assert "rollback" in events                   # the transaction rolled back
    assert "commit" not in events                  # ... and never committed
    assert not undo_path.exists()
    assert "error:" in capsys.readouterr().err


def test_a7_undo_out_dash_prints_the_json_between_the_markers(
        monkeypatch, capsys):
    # Spec: F-026c-registrar-research-import.md | AC-17
    """A-7: ``--undo-out -`` prints the record on stdout between the two
    markers (the production container run, where only stdout reaches the host)."""
    events = []
    mod = _fake_cli(monkeypatch, events)
    rc = asyncio.run(mod.cli(
        ["--apply", "--confirm-db", "epm_test", "--undo-out", "-"],
        research_text=FIXTURE.read_text(encoding="utf-8"),
    ))
    assert rc == 0, capsys.readouterr().err
    out = capsys.readouterr().out
    begin, end = ("=== F026C UNDO JSON BEGIN ===",
                  "=== F026C UNDO JSON END ===")
    assert begin in out and end in out
    payload = json.loads(out.split(begin, 1)[1].split(end, 1)[0])
    assert payload["feature"] == "F-026c"
    assert payload["database"] == "epm_test"
    assert payload["entries"][0]["id"] == 1
