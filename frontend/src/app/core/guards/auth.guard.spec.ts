import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { getStoredToken } from '../services/auth.service';
import { fakeExpiredJwt, fakeJwt } from '../testing/fake-jwt';
import { authGuard } from './auth.guard';

const TOKEN_KEY = 'abaco_token';

describe('authGuard (autenticação, não autorização)', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
    localStorage.clear();
  });

  afterEach(() => localStorage.clear());

  const run = () => TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));

  it('permite usuário autenticado (mesmo GUEST — autenticação ≠ autorização)', () => {
    localStorage.setItem(TOKEN_KEY, fakeJwt({ cargo: null }));
    expect(run()).toBe(true);
  });

  it('redireciona para /login sem token', () => {
    expect(run()).toBe('/login');
  });

  it('redireciona para /login com token expirado e limpa o storage', () => {
    localStorage.setItem(TOKEN_KEY, fakeExpiredJwt({ cargo: 1 }));
    expect(run()).toBe('/login');
    expect(getStoredToken()).toBeNull();
  });
});
