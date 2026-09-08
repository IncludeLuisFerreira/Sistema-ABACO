# Base do projeto + autenticação Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the monorepo foundation, Dockerized local environment, JWT login, and role-based access for the first ABACO delivery.

**Architecture:** Start with a minimal monorepo split into `backend/` and `frontend/`, each with its own TypeScript app and tests. The backend owns authentication, JWT issuance, and authorization middleware; the frontend owns the login form and a protected shell. PostgreSQL stays the source of truth for users, with manual inserts for the first users and bcrypt hashes for passwords.

**Tech Stack:** Node.js, Express, TypeScript, PostgreSQL, JWT, bcrypt, Next.js, TailwindCSS, Vitest, Supertest, Testing Library, Docker Compose.

---

### Task 1: Scaffold the monorepo and shared tooling

**Files:**
- Create: `package.json`
- Create: `tsconfig.base.json`
- Create: `.npmrc`
- Create: `backend/package.json`
- Create: `backend/tsconfig.json`
- Create: `backend/vitest.config.ts`
- Create: `backend/src/test/setup.ts`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`
- Modify: `.gitignore`

- [ ] **Step 1: Write the failing test**

Create a simple backend test file `backend/src/modules/auth/auth.service.test.ts` that imports `authenticateUser` from a file that does not exist yet and asserts it rejects invalid credentials.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test --workspace backend -- --runInBand backend/src/modules/auth/auth.service.test.ts`
Expected: FAIL because the backend workspace and auth service are not implemented yet.

- [ ] **Step 3: Write minimal implementation**

Create the workspace manifests, TypeScript base config, and test setup so the repository can compile the backend and frontend packages independently.

- [ ] **Step 4: Run test to verify the workspace is wired**

Run: `npm test --workspace backend -- --runInBand backend/src/modules/auth/auth.service.test.ts`
Expected: FAIL with the invalid-credentials assertion, but the workspace itself should now resolve imports and load the test runner correctly.

- [ ] **Step 5: Commit**

```bash
git add package.json tsconfig.base.json .npmrc backend frontend .gitignore
git commit -m "chore: scaffold monorepo foundation"
```

### Task 2: Implement backend authentication core

**Files:**
- Create: `backend/src/config/env.ts`
- Create: `backend/src/config/database.ts`
- Create: `backend/src/modules/auth/auth.types.ts`
- Create: `backend/src/modules/auth/auth.repository.ts`
- Create: `backend/src/modules/auth/auth.service.ts`
- Create: `backend/src/modules/auth/auth.controller.ts`
- Create: `backend/src/modules/auth/auth.routes.ts`
- Create: `backend/src/shared/middlewares/require-auth.ts`
- Create: `backend/src/shared/middlewares/require-role.ts`
- Create: `backend/src/shared/middlewares/error-handler.ts`
- Create: `backend/src/shared/utils/api-response.ts`
- Create: `backend/src/app.ts`
- Create: `backend/src/server.ts`
- Create: `backend/src/modules/auth/auth.service.test.ts`
- Create: `backend/src/shared/middlewares/require-auth.test.ts`
- Create: `backend/src/shared/middlewares/require-role.test.ts`

- [ ] **Step 1: Write the failing test**

Add tests that prove:

1. `authenticateUser(email, password)` returns a token for a valid bcrypt password.
2. `authenticateUser(email, password)` throws on invalid credentials.
3. `requireAuth` rejects requests without a bearer token.
4. `requireRole(['diretora'])` rejects a `professor`.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test --workspace backend -- --runInBand`
Expected: FAIL because the auth service, repository, and middleware are not implemented yet.

- [ ] **Step 3: Write minimal implementation**

Implement:

- env parsing for `DATABASE_URL`, `JWT_SECRET`, and `PORT`
- PostgreSQL connection helper
- repository lookup by email
- bcrypt password comparison
- JWT signing with `id`, `nome`, and `cargo`
- auth and role middleware
- global error handler
- route registration under `/api/auth`

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test --workspace backend -- --runInBand`
Expected: PASS for auth service and middleware tests.

- [ ] **Step 5: Commit**

```bash
git add backend/src
git commit -m "feat: add backend authentication core"
```

### Task 3: Build the frontend login and protected shell

**Files:**
- Create: `frontend/src/app/(auth)/login/page.tsx`
- Create: `frontend/src/app/(dashboard)/layout.tsx`
- Create: `frontend/src/app/(dashboard)/page.tsx`
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/services/auth.service.ts`
- Create: `frontend/src/hooks/useAuth.ts`
- Create: `frontend/src/components/layout/DashboardLayout.tsx`
- Create: `frontend/src/components/layout/Header.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/types/user.ts`
- Create: `frontend/src/app/(auth)/login/page.test.tsx`

- [ ] **Step 1: Write the failing test**

Add a login page test that renders the form, submits `email` and `senha`, and expects a redirect after a mocked successful authentication response.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test --workspace frontend -- --runInBand`
Expected: FAIL because the page, service layer, and protected layout are not implemented yet.

- [ ] **Step 3: Write minimal implementation**

Implement the login page, API wrapper, auth service, and dashboard shell so the frontend can call the backend and gate protected pages.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test --workspace frontend -- --runInBand`
Expected: PASS for the login flow and protected shell tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src
git commit -m "feat: add frontend login flow"
```

### Task 4: Wire Docker, database initialization, and environment defaults

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Create: `frontend/Dockerfile`
- Create: `frontend/.dockerignore`
- Create: `.env.example`

- [ ] **Step 1: Write the failing test**

Add a lightweight integration check script or container smoke test that expects `docker compose up --build` to expose the backend on `http://localhost:8000/`.

- [ ] **Step 2: Run test to verify it fails**

Run: `docker compose up --build`
Expected: FAIL until the Dockerfiles, compose file, and env defaults are wired correctly.

- [ ] **Step 3: Write minimal implementation**

Implement the three-container compose setup, mount the schema into Postgres initialization, and align backend/frontend container commands with the monorepo workspaces.

- [ ] **Step 4: Run test to verify it passes**

Run: `docker compose up --build`
Expected: containers start cleanly and the backend can reach PostgreSQL through the compose network.

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml backend/Dockerfile backend/.dockerignore frontend/Dockerfile frontend/.dockerignore .env.example database-schema.sql
git commit -m "feat: wire dockerized local environment"
```

### Task 5: Verify the first delivery end to end

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-04-27-base-projeto-autenticacao-design.md` only if a requirement changed during implementation

- [ ] **Step 1: Write the failing test**

Create one end-to-end login check using the real backend and frontend containers that logs in with a manually inserted user.

- [ ] **Step 2: Run test to verify it fails**

Run: `docker compose up --build` followed by the login check.
Expected: FAIL until the manual user is inserted with a bcrypt password hash and the JWT flow is working.

- [ ] **Step 3: Write minimal implementation**

Document the manual user insertion steps, expected cargo codes, and the command to boot the system locally.

- [ ] **Step 4: Run test to verify it passes**

Run: `docker compose up --build` and repeat the login check.
Expected: PASS with a valid `diretora`, `administrativo`, or `professor` user.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: document first auth delivery"
```

