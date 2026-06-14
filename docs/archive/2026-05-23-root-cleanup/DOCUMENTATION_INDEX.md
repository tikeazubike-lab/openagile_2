# OpenAgile Documentation Index

> **Central Registry** for all documentation across the OpenAgile infrastructure  
> Last Updated: 2026-01-28

---

## 📚 Documentation Structure

This index provides navigation to all documentation across projects and sub-projects in the OpenAgile ecosystem.

### Master Documents (Infrastructure-Level)

| Document | Location | Purpose |
|----------|----------|---------|
| **Infrastructure Contract** | [`INFRASTRUCTURE_CONTRACT.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/INFRASTRUCTURE_CONTRACT.md) | Canonical patterns for Traefik, networking, database integration |
| **Agent Coordination** | [`agents/`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/agents/) | Multi-agent workflow system (ORCHESTRATOR, INVESTIGATOR, BUILDER) |
| **Recovery Plan** | [`RECOVERY_PLAN.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/RECOVERY_PLAN.md) | Current recovery workflow for `thrive-tech-hub` |

---

## 🗂️ Project Documentation

### thrive-tech-hub (Ghost Portfolio + React Frontend)

**Project Manual**: [`thrive-tech-hub/PROJECT_MANUAL.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/PROJECT_MANUAL.md)

**Agent Guides**:
- [`AGENTS.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/AGENTS.md) - Overview of agent roles
- [`AGENT_FRONTEND.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/AGENT_FRONTEND.md) - React/Vite development (API integration)
- [`AGENT_BACKEND.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/AGENT_BACKEND.md) - Ghost infrastructure & Python automation

**Technical Documentation**:
- CI/CD: [`CI_CD_COMPLETE.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/CI_CD_COMPLETE.md)
- Deployment: [`docs/DEPLOYMENT_GUIDE.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/docs/DEPLOYMENT_GUIDE.md)
- Setup: [`docs/CI_CD_SETUP.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/docs/CI_CD_SETUP.md)
- Ghost API: [`docs/GHOST_INTEGRATION_GUIDE.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/docs/GHOST_INTEGRATION_GUIDE.md)

**Handoff**: [`docs/AGENT_HANDOFF.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/docs/AGENT_HANDOFF.md)

---

### frappe_docker (ERPNext Multi-Site Deployment)

**Project Manual**: [`frappe_docker/PROJECT_MANUAL.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/PROJECT_MANUAL.md)

**Core Documentation**:
- Master Doc: [`GEMINI_Frappe.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/GEMINI_Frappe.md)
- Troubleshooting: [`docs/custom_app_deployment_troubleshooting.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/docs/custom_app_deployment_troubleshooting.md)

**Deployment**:
- Script: [`deploy-compose.sh`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/deploy-compose.sh)
- CI/CD: [`.github/workflows/`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/.github/workflows/) (Docker image builds)

**Custom Apps**:
- [`apps/edu_theme/`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/apps/edu_theme/) - Vue.js 3 frontend
- [`apps/education/`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/apps/education/)
- [`apps/library_management/`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/apps/library_management/)

---

## 🔗 Cross-References

### Infrastructure Patterns
All projects must follow patterns defined in [`INFRASTRUCTURE_CONTRACT.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/INFRASTRUCTURE_CONTRACT.md):
- Network: `openagile_openagile_network` (Traefik integration)
- Certresolver: `cloudflare`
- Database naming conventions
- Volume mount patterns

### Deployment Workflows

| Project | Method | Documentation |
|---------|--------|---------------|
| **thrive-tech-hub** | GitHub Actions (push to `main`) | [`CI_CD_COMPLETE.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/CI_CD_COMPLETE.md) |
| **frappe_docker** | `deploy-compose.sh` (manual/remote trigger) | [`PROJECT_MANUAL.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/PROJECT_MANUAL.md) |

---

## 📝 Document Maintenance

### Adding New Documentation
1. Create document in appropriate project directory
2. Update this index with link and description
3. Add cross-references to related documents

### Updating Existing Documentation
1. Update the document content
2. Update "Last Updated" timestamp
3. Verify all backlinks still work

### Documentation Standards
- Use **markdown** format (`.md`)
- Include **file links** using absolute paths with `file://` protocol
- Use **alerts** (`> [!NOTE]`, `> [!WARNING]`, etc.) for critical information
- Maintain **bidirectional links** between parent and child docs

---

## 🚀 Quick Start Guides

**New to OpenAgile?**
1. Read: [`INFRASTRUCTURE_CONTRACT.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/INFRASTRUCTURE_CONTRACT.md)
2. Choose your project: [`thrive-tech-hub`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/PROJECT_MANUAL.md) or [`frappe_docker`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/PROJECT_MANUAL.md)
3. Review agent roles for your area

**Developer Workflow?**
- **Frontend**: [`thrive-tech-hub/AGENT_FRONTEND.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/AGENT_FRONTEND.md)
- **Backend**: [`thrive-tech-hub/AGENT_BACKEND.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub/AGENT_BACKEND.md)
- **Infrastructure**: [`INFRASTRUCTURE_CONTRACT.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/INFRASTRUCTURE_CONTRACT.md)
