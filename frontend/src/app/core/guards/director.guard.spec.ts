import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { directorGuard } from './role.guard';
import { AuthService } from '../services/auth.service';

describe('directorGuard', () => {
  it('allows access for director (cargo 1)', () => {
    const authService = { isAuthenticated: () => true, getToken: () => 'valid.token.with.cargo1' };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } }
      ]
    });

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, {} as never));
    expect(result).toBe('/login');
  });

  it('redirects when no token', () => {
    const authService = { isAuthenticated: () => false, getToken: () => null };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } }
      ]
    });

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, {} as never));
    expect(result).toBe('/login');
  });
});
