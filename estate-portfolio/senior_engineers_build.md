# How Senior Engineers Build with AI — Video Transcript Summary

> **Source**: YouTube video transcription (https://youtu.be/14RP8liACqo)
> **Speaker**: Adrian (JSM Mastery)
> **Core thesis**: Senior engineers in 2026 don't write code — they design systems and let AI handle implementation. The gap between developers who can do this and those who can't is dividing the industry.

---

## 1. The App Being Built: Ghost AI

**Ghost AI** is a real-time collaborative workspace where:
- Users describe a system in plain English
- An AI agent maps it onto a shared canvas live
- Teams edit the design together
- The app generates a complete technical specification document from the resulting graph

### Tech Stack
| Layer | Technology | Role |
|-------|-----------|------|
| Framework | Next.js + React 19 | Core framework |
| Real-time | Liveblocks | Collaborative canvas, presence, cursors |
| Background tasks | Trigger.dev | Long-running AI generation jobs |
| Auth | Clerk | User identity, route protection |
| Database | Prisma + Postgres | Metadata storage |
| Canvas | React Flow + Liveblocks React Flow | Node-based drag-and-drop canvas |
| Storage | Vercel Blob | Canvas snapshots, generated specs (Markdown) |
| AI | Google Gemini (via Vercel AI SDK) | Design generation + spec generation |
| UI | shadcn/ui + Tailwind CSS V4 | Component styling (dark theme only) |
| Code Review | CodeRabbit | AI-powered PR reviews |

---

## 2. Core Philosophy: Spec-Driven Development vs. Vibe Coding

### Vibe Coding (What Not to Do)
- Describe what you want → let the agent run → react to output
- Works for weekend prototypes, collapses for anything maintainable
- Result: new features break old ones, codebase contradicts itself, you spend more time untangling AI mistakes than building

### Spec-Driven Development (The Method)
- **You stay the architect**; the agent becomes the implementation engine
- Figure out what you're building *before* you build it
- Write specs → give spec to agent in one prompt → review against checklist → ship or fix with focused corrective prompt

### Two Prompts Compared

**Vague (bad):** "Build me a SaaS app with authentication and a real-time canvas."

**Spec-driven (good):** "I'm adding a Liveblocks room provider to the workspace route. Auth is already handled by Clerk middleware. The canvas uses React Flow. Room tokens should be issued only after verifying project membership. Wire the provider into the existing workspace layout without touching the sidebar or navbar."

The AI isn't smarter reading the second prompt — the **developer is**.

---

## 3. The Six-File Context System

Created in a `/context` folder at project root. These files are loaded by the AI agent before every session. The approach mirrors how Google, Amazon, and Netflix operate — engineers spend weeks writing design docs before writing production code.

### File 1: `project-overview.md`
- One-paragraph summary + numbered goals (concrete and measurable)
- Core user flow (sign-in → project creation → design architecture → spec generation)
- Technology choices justified (e.g., Clerk over custom auth because shipping speed matters, security is better, agent skills exist)
- **Scope section** — in-scope vs. out-of-scale features (critical for keeping builds focused; tells the agent "don't even think about" billing, enterprise permissions, version history)
- Success criteria — benchmarks to verify after each major feature

### File 2: `architecture.md`
- Tech stack with role per technology
- System boundaries (API routes vs. background jobs vs. storage)
- **Hybrid storage model**: Postgres for metadata, Vercel Blob for actual files (canvas JSON, markdown specs) — keeps the database lean
- Integration rules (e.g., project membership must be verified before issuing Liveblocks tokens)
- **Invariants** — rules the system must never violate:
  - Request handlers do not run long-lived AI work
  - Metadata and large artifacts stored in separate layers
  - Auth and ownership enforced at every mutation boundary
  - Client components only used when needed
  - Canvas schema must remain consistent

### File 3: `code-standards.md`
- Strict TypeScript (avoid `any`)
- `use client` only when component needs browser interactivity
- No raw Tailwind color classes — reference CSS custom property tokens through Tailwind utility names
- Consistent API route patterns
- Consistent Next.js conventions

### File 4: `ai-workflow-rules.md**
- **Most important rule**: work on one feature unit at a time
- Don't combine unrelated system boundaries in a single implementation step
- Defines how to scope work and what to do when a decision is needed

### File 5: `ui-context.md`
- Design tokens (colors, fonts, border radii)
- Dark mode only — all colors predefined so the agent doesn't guess
- Font families, sizing conventions
- Described aesthetic to AI: "dark, technical, precise, feels like an engineering tool" — AI generated the palette through back-and-forth conversation

### File 6: `progress-tracker.md`
- The **only file that updates constantly** throughout the build
- Current phase, what's in progress, what's complete, what's next
- Architectural decisions and session notes
- How the agent picks up exactly where you left off in a single prompt — solves the "AI has no memory between sessions" problem

### Entry Point: `agents.md`
- Wires all six files together
- Instructions for the agent: read all context files in order before implementing anything; update the progress tracker after each change
- Placed at project root (or uses `claude.md`, `cursorrules`, etc. depending on agent)

---

## 4. The Build Workflow (Step by Step)

### Phase 0: Conceptual Design
1. Open a planning AI (ChatGPT, Claude, Gemini)
2. Talk through the idea: what does it do, who uses it, core flows, complex patterns, what could go wrong
3. Push back on answers — let AI pressure-test your thinking
4. This conversation IS the work; when the system is clear in your head, write it down

### Phase 1: Project Scaffolding
```
npx create-next-app@latest  →  React, TypeScript, ESLint, Tailwind, App Router
```
Then clean boilerplate (first interaction with coding agent)

### Phase 2: Write Context Files
Create the six context files through conversation with planning AI. Use the free template as starting point. Generate them for YOUR project by describing requirements to AI.

### Phase 3: Create Feature Specs
- Create a `/context/feature-specs/` folder
- Each feature gets its own spec file: `01-design-system.md`, `02-editor.md`, etc.
- Spec structure:
  - **Goal**: 1-2 sentences — what does this unit produce when done?
  - **Design decisions**: visual/structural specifics, refers to UI context
  - **Implementation details**: component names, file paths, specific behaviors
  - **Dependencies**: what needs to be installed/configured first
  - **Checklist**: concrete verification criteria (TypeScript passes, no lint errors, specific behavior works)

### Phase 4: Execute Each Spec
For each feature:
1. Open a NEW chat with the coding agent (prevents stale context)
2. Prompt: "Read [spec-file.md], update the progress-tracker.md to mark this as in progress, then implement exactly as specified."
3. Agent reads the spec + context files, plans, updates progress tracker, implements
4. Review against checklist
5. If it passes: close unit, `git commit`, push, move to next spec
6. If something's off: write focused corrective prompt ("exactly what's wrong, exactly what you expect, fix that specific thing")

### Phase 5: Debug with `current-issues.md`
- When bugs appear, create `/context/current-issues.md`
- Document the error, what action triggered it, paste terminal error
- Ask agent to analyze and provide fix plan FIRST, then approve execution
- This prevents the "fix spiral" where AI breaks 10 things while fixing one
- Never commit this file to Git (add to `.gitignore`)

---

## 5. Development Tools & Agent Skills

### AI Coding Agent (Tool-Agnostic)
The video is agent-agnostic. Options mentioned:
- **Claude Code** (recommended; creator's choice at JSM)
- **OpenAI Codex** (budget: Go plan or Plus plan)
- **Cursor, Windsurf, GitHub Copilot** (anything works)

### Agent Skills Pattern
A recurring pattern for every major library:
1. Install the library
2. Get API keys / configure environment variables
3. Install agent skills: `npx skills add <library>-skills`
4. Select relevant skill packages (e.g., "Clerk Next.js patterns", "Prisma Postgres setup", "Liveblocks best practices")
5. Agent now has domain-specific knowledge for that library

Libraries with agent skills used: Clerk, Prisma, Liveblocks, Trigger.dev

### Model Choice
- Default: Opus (large context, expensive)
- Recommended: **Sonnet** — fast, inexpensive, works well WITH context files; without context files it can get lost
- For code tasks, context files matter more than model choice

### Voice Prompting
- Use Whisper Flow (or built-in microphone) to speak prompts — faster than typing
- In Claude Code: hold Command+D to speak

---

## 6. Build Sequence (Features Implemented in Order)

### Feature 01: Design System
- Install shadcn/ui with dark theme
- Add components: button, dialog, tabs, input, textarea, etc.
- Install lucide-react for icons
- Create `lib/utils.ts` with `cn()` helper for merging Tailwind classes

### Feature 02: Editor Chrome
- Editor navbar (fixed height, left/center/right sections)
- Project sidebar (floats above canvas, slides in, uses shadcn tabs)
- Dialog pattern component (title, description, footer actions)
- Git push → PR → CodeRabbit review → merge to main

### Feature 03: Authentication (Clerk)
- Install `@clerk/nextjs`, set up `.env.local` with Clerk keys
- **Next.js 16 gotcha**: use `proxy.ts` not `middleware.ts` (most agents trained on v14/15 will get this wrong — must specify explicitly)
- Middleware: define public routes explicitly, protect everything else
- Wrap root layout with ClerkProvider (dark theme)
- Sign-in/sign-up pages: two-panel layout (logo+tagline left, Clerk form right)
- Redirect authenticated users → editor; unauthenticated → sign-in
- Add UserButton to editor navbar
- **Debugging pattern**: create `current-issues.md`, describe logout error and sign-up redirect loop → agent analyzes → identifies missing `afterSignOutUrl` and `afterSignUpUrl` env vars → fixes
- CodeRabbit catches: exposed JWT in `current-issues.md` file → add to `.gitignore`

### Feature 04: Project Dialogues
- Create/rename/delete dialogues in sidebar
- Mock project data (no API yet)
- Centralized hook (`use-project-dialogues.ts`) managing dialogue state
- Slug auto-generation from project name
- Sidebar shows rename/delete only for owned projects, hides for shared
- CodeRabbit catches: empty slug edge case (all special characters) → accept fix in VS Code extension

### Feature 05: Prisma + Postgres
```bash
npm install prisma tsx @types/pg --save-dev
npm install @prisma/client prisma-adapter-pg dotenv pg
npx prisma init --output data/app/generated/prisma
```
- **Prisma Agent Skills**: `npx skills add prisma-skills`
- Dashboard: prisma.com → create project → get connection string
- Models: `Project` (ownerId, name, description, status enum, canvas blob URL, timestamps), `ProjectCollaborator` (projectId, email, timestamps, cascading delete)
- Prisma client singleton with Accelerate adapter
- CodeRabbit catches: `current-issues.md` committed (security issue)

### Feature 06: Project CRUD API
- Wire create/read/update/delete for projects using Prisma
- Replace mock data in dialogues with real API calls

### Feature 07: Protected Workspace Route
- Guard `/editor/[projectId]` route server-side
- Check project membership before rendering
- Non-members see "access denied" with back button

### Feature 08: Collaborative Canvas (Liveblocks Setup)
```bash
npm install @liveblocks/client @liveblocks/react @liveblocks/react-ui @liveblocks/react-flow xyflow
npx liveblocks init
```
- **Liveblocks Agent Skills**: `npx skills add liveblocks-skills`
- `liveblocks.config.ts`: define presence types (cursor position, user color, thinking state)
- Create `lib/liveblocks.ts`: cached client with user color mapping
- Auth endpoint: `POST /api/liveblocks-auth` — verifies Clerk auth + project membership
- Set Liveblocks keys in `.env.local`

### Feature 09: Share Dialog
- Share button in workspace navbar
- Invite collaborators by email
- View/remove current collaborators
- Copy project link with clipboard feedback (and error handling)
- Use Clerk Backend API to enrich collaborator emails with display name/avatar
- Ownership enforced server-side, not client-side
- CodeRabbit catches: clipboard API failure handling, batch Clerk user fetch limit (500)

### Feature 10-12: Canvas Base + Shape Panel
- Replace placeholder with Liveblocks-backed ReactFlow canvas
- Floating shape panel at bottom: rectangle, diamond, circle, pill, cylinder, hexagon
- Drag-and-drop shapes onto canvas
- **Debugging drag-and-drop**: Liveblocks storage schema requires nested `flow` key for nodes/edges, not top-level. Agent skills help identify this.
- Fix: move `onDragOver`/`onDrop` from ReactFlow to wrapper div; fix storage path to `storage.flow.nodes`

### Features 13-17: Canvas Polish
- **13 Node Shapes**: SVG-based shape rendering per type, drag preview ghost
- **14 Node Editing**: Resize handles (XY Flow), inline label editing (double-click → contentEditable)
- **15 Node Colors**: Floating color toolbar on selection, 6-8 predefined colors with auto text contrast
- **16 Edge Behavior**: Custom edges with connection handles on all 4 sides, edge labels
- **17 Canvas Ergonomics**: Zoom in/out/fit view controls, undo/redo (Cmd+Z/Y), remove minimap
- Each feature: new spec file → new chat → implement → verify → push

### Feature 18: Starter Templates
- Template library: microservices, CI/CD pipeline, event-driven system
- Pre-built diagrams importable into canvas
- Template preview cards with SVG thumbnails
- Screenshot-based visual feedback for design corrections

### Features 19-21: Collaboration + Persistence
- **19 Presence**: Live cursors with name/color, stacked avatar group in navbar
- **20 AI Sidebar**: Right sidebar placeholder (AI Architect tab + Specs tab), chat UI without backend
- **21 Canvas Autosave**: Save canvas state to Vercel Blob on every change, store blob URL in Prisma
  - Vercel Blob setup: private storage, `BLOB_READ_WRITE_TOKEN`
  - Save button in navbar (Save → Saving → Saved state machine)
  - Fix stale Prisma client cache issue, fix `allowOverwrite: true` for re-saves

### Features 22-26: AI Design Agent
- **Trigger.dev setup**: `npx trigger.dev@latest init`, create project, set `.env.local` keys (`TRIGGER_PROJECT_REF`, `TRIGGER_SECRET_KEY`)
  - Local worker: `npx trigger.dev@latest dev` (must run alongside Next.js dev server)
  - Max duration: 3600s, retries: 3 with exponential backoff
  - **Trigger Agent Skills**: `npx skills add trigger.dev-skills`
- Packages: `@trigger.dev/react-hooks` (subscribe to live run status), `@ai-sdk/google` (Gemini provider), `ai` (Vercel AI SDK)
- **22 Design Agent API**: auth route → create task run record → trigger background task
- **23 Design Agent Logic**: Gemini prompt → structured canvas actions (add/move/resize/update/delete nodes and edges) → apply via Liveblocks storage mutation
  - Gotcha: `generateText` with `output.object` API experimental → replaced with tool-calling approach (each action = named tool) for schema compliance
  - AI presence: `thinking: true` cursor, status broadcasts (start/thinking/complete)
- **24 AI Presence State**: Shared activity indicator, thinking spinner cursor, disabled input during generation
- **25 Sidebar Chat**: Liveblocks Feeds for real-time message sync across clients
- **26 Wire Together**: AI sidebar submits prompt → API returns run ID → Trigger.dev hook tracks live → status updates in sidebar → canvas updates auto via Liveblocks
  - Debug: eager validation check for access token → only validate when active run exists

### Features 27-29: Spec Generation
- **27 Spec Generation Flow**: Trigger route → background task reads canvas nodes/edges + chat history → Gemini generates Markdown technical spec → returns markdown text
- **28 Spec Persistence/Download**: Save spec to Vercel blob, store URL in `ProjectSpec` Prisma model, secure download API route (auth + ownership check)
- **29 Spec UI Integration**: List generated specs in sidebar tab, markdown preview modal, download button

---

## 7. Code Review Workflow

### CodeRabbit Integration
1. Push code to `development` branch
2. Open PR → CodeRabbit auto-reviews
3. Review comments directly in VS Code via CodeRabbit extension
4. Fix issues (accept in-place or use agent)
5. Merge to main

### Types of Issues Caught
- Accessibility: icon buttons missing `aria-label`
- Double-commit bugs: Enter/Blur handlers both firing mutations
- React 19 ref compatibility: move ref updates into sync effects
- Security: tokens/URLs committed to repo → add to `.gitignore`
- Edge cases: caps lock not handled in keyboard shortcuts, empty slug validation

### Branching Strategy
- `main`: production code
- `development`: active feature development
- Each feature → development branch → PR → review → merge to main

---

## 8. Deployment to Vercel

### Pre-Deployment Checklist
1. Switch Liveblocks: create production project → copy prod keys → update `.env.local`
2. Switch Trigger.dev: toggle to production in dashboard → copy prod secret key
3. Verify ALL environment variables are present (Clerk, Liveblocks, Trigger, Prisma, Vercel Blob, Google AI)
4. Final PR: development → main

### Deployment
1. Import Git repo in Vercel
2. Paste all env vars
3. Deploy

### Common Deployment Fixes
- **npm install fails**: delete `package-lock.json`, push fresh
- **Prisma fails in build**: add `postinstall` script in `package.json`: `"postinstall": "prisma generate"`
- Third deployment attempt succeeded for this project

---

## 9. Key Patterns & Lessons

### The Golden Rule
> "The clearer your understanding of what you're building, the better the AI output. Learning properly isn't a waste of time in the AI era — it's the best investment."

### Architectural Decisions Worth Noting
1. **Hybrid storage**: Postgres for metadata + Vercel Blob for files (keeps DB lean)
2. **Background tasks for AI**: Never run AI generation in API routes (timeout risk); use Trigger.dev for durable background execution
3. **Agent skills over documentation**: Install official agent skills for every major library — gives the agent current API knowledge
4. **Spec files over prompts**: Feature specs in markdown files are reusable, reviewable, and precise — better than one-off chat messages
5. **Separate chats per feature**: Start fresh chat for each spec to reduce context bloat and increase focus
6. **New chat vs. same chat**: New chat for new features; same chat only for follow-up fixes to existing features
7. **Debug with analysis first**: Ask agent to analyze and provide fix plan before executing — prevents cascading breakage
8. **Two-panel design layout**: Split screen for auth (branding left, form right) = professional SaaS look
9. **Dark mode only**: Reduces theme complexity for the agent

### What Makes This Different from Other AI Build Tutorials
The creator used the **same methodology to build the tool that the app itself teaches**. The app exists to help teams do spec-driven development — and the app itself was built with spec-driven development.

### Token Efficiency
- Context files cost some tokens upfront but save 10x in reduced back-and-forth
- Keep chats focused to save tokens
- New Agent = fresh context window = better output

---

## 10. Complete File Structure

```
ghost-ai/
├── agents.md                    # Entry point (tells agent to load context/)
├── context/
│   ├── project-overview.md      # Product definition, goals, scope
│   ├── architecture.md          # Tech stack, boundaries, invariants
│   ├── code-standards.md        # TypeScript/Next.js conventions
│   ├── ai-workflow-rules.md     # How the agent should behave
│   ├── ui-context.md            # Design tokens, colors, fonts
│   ├── progress-tracker.md      # Current state of the build
│   ├── current-issues.md        # Active bugs (gitignored)
│   └── feature-specs/
│       ├── 01-design-system.md
│       ├── 02-editor.md
│       ├── 03-auth.md
│       ├── 04-project-dialogues.md
│       ├── 05-prisma.md
│       ├── 06-project-crud.md
│       ├── 07-workspace-route.md
│       ├── 08-liveblocks-setup.md
│       ├── 09-share-dialog.md
│       ├── 10-liveblocks-infra.md
│       ├── 11-base-canvas.md
│       ├── 12-shape-panel.md
│       ├── 13-node-shape.md
│       ├── 14-node-editing.md
│       ├── 15-node-color-toolbar.md
│       ├── 16-edge-behavior.md
│       ├── 17-canvas-ergonomics.md
│       ├── 18-starter-templates.md
│       ├── 19-presence-avatars.md
│       ├── 20-ai-sidebar.md
│       ├── 21-canvas-autosave.md
│       ├── 22-design-agent-api.md
│       ├── 23-design-agent-logic.md
│       ├── 24-ai-presence-state.md
│       ├── 25-sidebar-chat-feed.md
│       ├── 26-design-agent-wiring.md
│       ├── 27-spec-generation-flow.md
│       ├── 28-spec-persistence-download.md
│       └── 29-spec-ui-integration.md
├── prisma/
│   └── schema.prisma
├── trigger/
│   └── design-agent.ts
├── app/
├── components/
├── lib/
├── .env.local
└── package.json
```
