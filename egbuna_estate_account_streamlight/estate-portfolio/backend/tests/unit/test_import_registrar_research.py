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
from pathlib import Path

import pytest

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
    assert head[0].sort_order == 1


def test_field_sort_orders_step_by_10_after_existing_fields():
    # Spec: F-026c-registrar-research-import.md | AC-7
    """Head office address sorts first (1); everything else steps by 10
    after the existing fields (the existing max sort_order on #1 is 10)."""
    plan = _build()
    alpha = _fields(plan, 1)
    head = [op for op in alpha if op.field_value == "1 Alpha Way, Lagos"][0]
    rest = [op.sort_order for op in alpha if op is not head]
    assert rest == sorted(rest)
    assert all(order % 10 == 0 for order in rest)
    assert min(rest) == 20                       # existing fields end at 10

    newbies = _fields(plan, ("new", "newbies"))
    head2 = [op for op in newbies
             if op.field_value == "5 Newbie Close, Ikeja, Lagos"][0]
    rest2 = [op.sort_order for op in newbies if op is not head2]
    assert min(rest2) == 10                      # no pre-existing fields


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
    monkeypatch.delenv("DATABASE_URL", raising=False)
    rc = asyncio.run(amain(["--apply", "--confirm-db", "epm_test"]))
    assert rc != 0


def test_apply_without_confirm_db_refuses_before_touching_anything():
    # Spec: F-026c-registrar-research-import.md | AC-14
    rc = asyncio.run(amain(["--apply"]))
    assert rc != 0
