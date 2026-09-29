import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { roleGuard } from './role.guard';

function makeToken(payload: Record<string, unknown>): string {
  return `header.${btoa(JSON.stringify(payload))}.signature`;
}

function futureExp(): number {
  return Math.floor(Date.now() / 1000) + 3600;
}

describe('roleGuard', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
  });

  afterEach(() => localStorage.clear());

  it('allows access when user has an allowed cargo', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '1', cargo: 1, exp: futureExp() }));

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, { url: '/admin/home' } as never));

    expect(result).toBe(true);
  });

  it('redirects to access denied when cargo is not allowed', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '2', cargo: 2, exp: futureExp() }));

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, { url: '/admin/home' } as never));

    expect(result).toBe('/acesso-negado');
  });

  it('redirects unauthenticated users to login', () => {
    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, { url: '/admin/home' } as never));

    expect(result).toBe('/login');
  });

  it('redirects first access users to change password', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '2', cargo: 2, primeiro_acesso: true, exp: futureExp() }));

    const guard = roleGuard([2]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, { url: '/academico' } as never));

    expect(result).toBe('/alterar-senha');
  });
});
