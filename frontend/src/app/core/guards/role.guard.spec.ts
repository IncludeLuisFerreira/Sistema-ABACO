import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AppRole, AuthService } from '../services/auth.service';
import { roleGuard } from './role.guard';

class FakeAuthService {
  private _authenticated = false;
  private _role: AppRole | null = null;

  isAuthenticated() {
    return this._authenticated;
  }

  hasRole(allowedRoles: AppRole[]) {
    return this._role !== null && allowedRoles.includes(this._role);
  }

  setSession(authenticated: boolean, role: AppRole | null = null) {
    this._authenticated = authenticated;
    this._role = role;
  }
}

describe('roleGuard', () => {
  it('allows access when user has an allowed role', () => {
    const authService = new FakeAuthService();
    authService.setSession(true, 'DIRECTOR');

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } },
      ],
    });

    const guard = roleGuard(['DIRECTOR', 'ADMIN']);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe(true);
  });

  it('redirects to login when user does not have an allowed role', () => {
    const authService = new FakeAuthService();
    authService.setSession(true, 'TEACHER');

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } },
      ],
    });

    const guard = roleGuard(['DIRECTOR', 'ADMIN']);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe('/login');
  });

  it('redirects unauthenticated users to login', () => {
    const authService = new FakeAuthService();
    authService.setSession(false);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } },
      ],
    });

    const guard = roleGuard(['DIRECTOR', 'ADMIN']);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe('/login');
  });
});
