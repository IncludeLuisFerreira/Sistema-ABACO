# Frontend Angular Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize the Angular frontend around the current standalone setup, preserving the existing folder structure while enforcing lazy-loaded feature routes, shared UI primitives, global interceptors, and ABACO theme variables.

**Architecture:** The app will stay standalone and use `app.config.ts` plus router-level lazy loading as the composition root. The existing `core`, `shared`, and `features` folders will be kept, and the current shell will act as the page frame instead of introducing a new AppModule or a separate layouts tree. Global cross-cutting concerns will live in `core`, reusable UI in `shared`, and route-driven screens in `features`.

**Tech Stack:** Angular 21 standalone APIs, TypeScript, SCSS, RxJS, HTTP interceptors, router lazy loading, and the existing Angular test setup.

---

### Task 1: Global app composition and routes

**Files:**
- Modify: `frontend/src/app/app.config.ts`
- Modify: `frontend/src/app/app.routes.ts`
- Modify: `frontend/src/app/app.ts`
- Modify: `frontend/src/app/app.html`

- [ ] **Step 1: Add router and HTTP providers needed for the standalone shell**

```ts
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { tokenInterceptor } from './core/interceptors/token.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([tokenInterceptor, errorInterceptor]))
  ]
};
```

- [ ] **Step 2: Define lazy routes for login, academico, logistico, and admin**

```ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/pages/login/login').then(m => m.Login)
  },
  {
    path: 'academico',
    loadChildren: () => import('./features/academico/academico.routes').then(m => m.ACADEMICO_ROUTES)
  },
  {
    path: 'logistico',
    loadChildren: () => import('./features/logistico/logistico.routes').then(m => m.LOGISTICO_ROUTES)
  },
  {
    path: 'admin',
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES)
  },
  { path: '**', redirectTo: 'login' }
];
```

- [ ] **Step 3: Keep the root shell minimal and router-only**

```ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {}
```

```html
<router-outlet></router-outlet>
```

- [ ] **Step 4: Run the frontend build to confirm the route tree compiles**

Run: `npm run build` from `frontend/`
Expected: build succeeds with no missing-route or standalone-import errors.

### Task 2: Core HTTP and error handling

**Files:**
- Modify: `frontend/src/app/core/interceptors/token.interceptor.ts`
- Create: `frontend/src/app/core/interceptors/error.interceptor.ts`
- Create: `frontend/src/app/core/services/notification.service.ts`
- Modify: `frontend/src/app/app.config.ts`

- [ ] **Step 1: Convert the token interceptor to the Angular functional HTTP interceptor API**

```ts
import { HttpInterceptorFn } from '@angular/common/http';

export const tokenInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('abaco_token');
  if (!token) {
    return next(req);
  }

  return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
};
```

- [ ] **Step 2: Add a global error interceptor that forwards API errors to a notification service**

```ts
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { NotificationService } from '../services/notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if ([401, 403, 409].includes(error.status)) {
        notifications.error(error.error?.detail || error.message || 'Erro ao processar a requisição.');
      }

      return throwError(() => error);
    })
  );
};
```

- [ ] **Step 3: Add a lightweight notification service for centralized user alerts**

```ts
import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  readonly message = signal<string | null>(null);

  error(message: string): void {
    this.message.set(message);
  }

  clear(): void {
    this.message.set(null);
  }
}
```

- [ ] **Step 4: Register the interceptors through the standalone provider stack**

```ts
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { errorInterceptor } from './core/interceptors/error.interceptor';
import { tokenInterceptor } from './core/interceptors/token.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([tokenInterceptor, errorInterceptor]))
  ]
};
```

- [ ] **Step 5: Run the relevant frontend build to catch interceptor typing issues**

Run: `npm run build`
Expected: build succeeds and the interceptor pipeline is accepted by the compiler.

### Task 3: Shared UI and theme tokens

**Files:**
- Modify: `frontend/src/styles.scss`
- Modify: `frontend/src/app/shared/components/primary-button/primary-button.ts`
- Modify: `frontend/src/app/shared/components/primary-button/primary-button.html`
- Modify: `frontend/src/app/shared/components/primary-button/primary-button.scss`
- Modify: `frontend/src/app/features/auth/pages/login/login.ts`

- [ ] **Step 1: Move ABACO theme tokens into CSS variables and keep the global stylesheet minimal**

```scss
:root {
  --color-primary: #f2a93b;
  --color-secondary: #595959;
  --color-surface: #ffffff;
  --color-background: #f9f9f9;
  --color-danger: #d93025;
  --font-family-base: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

html,
body {
  height: 100%;
  margin: 0;
  background: var(--color-background);
  color: var(--color-secondary);
  font-family: var(--font-family-base);
}
```

- [ ] **Step 2: Keep the primary button as the shared visual test component**

```ts
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ab-primary-button',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './primary-button.html',
  styleUrls: ['./primary-button.scss']
})
export class PrimaryButton {
  @Input() disabled = false;
  @Input() label = 'Entrar';
}
```

```html
<button type="submit" class="primary" [disabled]="disabled">{{ label }} <ng-content></ng-content></button>
```

```scss
.primary {
  margin-top: 1rem;
  width: 100%;
  background: var(--color-primary);
  color: #fff;
  padding: 0.75rem;
  border-radius: 6px;
  border: 0;
  font-weight: 600;
}

.primary[disabled] {
  opacity: 0.6;
}
```

- [ ] **Step 3: Use the shared button and theme tokens in the login page without introducing new global styles**

```ts
import { PrimaryButton } from '../../../../shared/components/primary-button/primary-button';

@Component({
  standalone: true,
  imports: [PrimaryButton]
})
export class Login {}
```

- [ ] **Step 4: Build the frontend and verify shared component imports still resolve**

Run: `npm run build`
Expected: build succeeds and the shared button remains importable from the auth feature.

### Task 4: Route shells for business domains

**Files:**
- Create: `frontend/src/app/features/academico/academico.routes.ts`
- Create: `frontend/src/app/features/admin/admin.routes.ts`
- Create: `frontend/src/app/features/logistico/logistico.routes.ts`
- Create: `frontend/src/app/features/academico/pages/home/home.ts`
- Create: `frontend/src/app/features/admin/pages/home/home.ts`
- Create: `frontend/src/app/features/logistico/pages/home/home.ts`

- [ ] **Step 1: Add one lightweight standalone page per business domain**

```ts
import { Component } from '@angular/core';

@Component({
  standalone: true,
  selector: 'app-academico-home',
  template: '<p>Academico</p>'
})
export class AcademicoHome {}
```

- [ ] **Step 2: Export route arrays from each domain file using lazy-loaded standalone components**

```ts
import { Routes } from '@angular/router';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/home/home').then(m => m.AdminHome)
  }
];
```

- [ ] **Step 3: Confirm the domain routes are reachable from the router without direct imports in the app shell**

Run: `npm run build`
Expected: route files compile and no feature screen is eagerly imported from the root.

### Task 5: Smoke tests and cleanup

**Files:**
- Modify: `frontend/src/app/app.spec.ts`
- Modify: `frontend/src/app/shared/components/primary-button/primary-button.ts` if needed for testability
- Modify: `frontend/src/app/core/interceptors/*.ts` if typing cleanup is needed

- [ ] **Step 1: Add a smoke test for the shared button rendering**

```ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PrimaryButton } from './primary-button';

describe('PrimaryButton', () => {
  let fixture: ComponentFixture<PrimaryButton>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [PrimaryButton] }).compileComponents();
    fixture = TestBed.createComponent(PrimaryButton);
    fixture.componentRef.setInput('label', 'Salvar');
    fixture.detectChanges();
  });

  it('renders the configured label', () => {
    expect(fixture.nativeElement.textContent).toContain('Salvar');
  });
});
```

- [ ] **Step 2: Add a minimal router smoke test for the login redirect**

```ts
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';

describe('app routes', () => {
  it('includes a login route and default redirect', () => {
    TestBed.configureTestingModule({ providers: [provideRouter(routes)] });
    expect(routes.some(route => route.path === 'login')).toBeTrue();
  });
});
```

- [ ] **Step 3: Run the focused frontend test suite and the build**

Run: `npm test -- --watch=false` and `npm run build`
Expected: test suite passes and the application builds successfully.
