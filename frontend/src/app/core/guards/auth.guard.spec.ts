import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';

class FakeAuthService {
  private _authenticated = false;

  isAuthenticated() {
    return this._authenticated;
  }

  setAuthenticated(value: boolean) {
    this._authenticated = value;
  }
}

describe('authGuard', () => {
  it('allows access for authenticated users', () => {
    const authService = new FakeAuthService();
    authService.setAuthenticated(true);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } }
      ]
    });

    const result = TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));

    expect(result).toBe(true);
  });

  it('redirects unauthenticated users to login', () => {
    const authService = new FakeAuthService();
    authService.setAuthenticated(false);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: { parseUrl: (url: string) => url } }
      ]
    });

    const result = TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));

    expect(result).toBe('/login');
  });
});
