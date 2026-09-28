import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { authGuard } from './auth.guard';

function makeToken(payload: Record<string, unknown>): string {
  return `header.${btoa(JSON.stringify(payload))}.signature`;
}

function futureExp(): number {
  return Math.floor(Date.now() / 1000) + 3600;
}

describe('authGuard', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
  });

  afterEach(() => localStorage.clear());

  it('allows access for authenticated users', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '1', cargo: 1, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/admin/home' } as never)
    );

    expect(result).toBe(true);
  });

  it('redirects unauthenticated users to login', () => {
    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/admin/home' } as never)
    );

    expect(result).toBe('/login');
  });

  it('redirects first access users to the change password screen', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '1', cargo: 2, primeiro_acesso: true, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/academico' } as never)
    );

    expect(result).toBe('/alterar-senha');
  });

  it('allows first access users to reach the change password screen', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '1', cargo: 2, primeiro_acesso: true, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/alterar-senha' } as never)
    );

    expect(result).toBe(true);
  });
});
