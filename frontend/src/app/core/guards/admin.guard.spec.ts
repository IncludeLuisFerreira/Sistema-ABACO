import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { adminGuard } from './role.guard';
import { AuthService } from '../services/auth.service';

describe('adminGuard', () => {
  it('redirects when no token', () => {
    const authService = { isAuthenticated: () => false, getToken: () => null };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } }
      ]
    });

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
    expect(result).toBe('/login');
  });

  it('redirects with malformed token', () => {
    const authService = { isAuthenticated: () => true, getToken: () => 'malformed' };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } }
      ]
    });

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
    expect(result).toBe('/login');
  });
});
