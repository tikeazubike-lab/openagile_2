import os

DOMAIN_FOLDERS = {
    "AUTH": "auth", "HOLD": "holdings", "PRIC": "prices", "PRIH": "price-history",
    "DASH": "dashboard", "REGR": "registrars", "CLAM": "claims", "DIVD": "dividends",
    "TRAN": "transactions", "NAVH": "nav-history", "WTCH": "watchlist",
    "COMP": "companies", "ADMN": "admin", "USER": "admin/users",
    "OBSD": "admin/obsidian", "CHAT": "chat", "SEC": "../security", "INF": "../infrastructure",
}


def test_id_to_path(test_id: str, base_path: str):
    """Convert a test ID like 'HOLD-CREATE-BE-INT-001' to an absolute file path and directory."""
    parts = test_id.split("-")
    if len(parts) != 5:
        raise ValueError(f"Invalid test ID format: {test_id}")

    domain_code = parts[0]
    workflow = parts[1].lower()
    layer = parts[2].lower()
    test_type = parts[3].lower()

    folder = DOMAIN_FOLDERS.get(domain_code)
    if not folder:
        raise ValueError(f"Unknown domain code: {domain_code}")

    test_dir = os.path.join(base_path, "backend", folder, workflow, test_type)
    test_file = os.path.join(test_dir, f"{test_id}.py")
    return test_file, test_dir


def generate_test_stub(test_id: str, domain_code: str, workflow: str, layer: str,
                       test_type: str, title: str, requirement_ref: str = "") -> str:
    """Generate pytest stub file content with docstring header and failing assertion."""
    func_name = test_id.replace("-", "_").lower()

    req_line = f'Requirement: {requirement_ref}' if requirement_ref else ''

    lines = [
        '"""',
        f'Test ID:     {test_id}',
        f'Title:       {title}',
        f'Domain:      {domain_code}',
        f'Workflow:    {workflow}',
        f'Layer:       {layer}',
        f'Type:        {test_type}',
    ]
    if req_line:
        lines.append(req_line)
    lines.append('"""')
    lines.append('')
    lines.append('')
    lines.append(f'async def test_{func_name}():')
    lines.append('    # TODO: implement test logic')
    lines.append('    assert False  # TODO: implement')
    lines.append('')
    return "\n".join(lines)
