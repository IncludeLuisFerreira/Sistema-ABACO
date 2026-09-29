import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { roleGuard } from './role.guard';

function makeToken(payload: Record<string, unknown>): string {
  const encoded = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
  return `header.${encoded}.signature`;
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

  afterEach(() => {
    localStorage.clear();
  });

  it('allows access when the token cargo is allowed', () => {
    localStorage.setItem('abaco_token', makeToken({ cargo: 1, exp: futureExp() }));

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe(true);
  });

  it('redirects to access denied when the token cargo is not allowed', () => {
    localStorage.setItem('abaco_token', makeToken({ cargo: 2, exp: futureExp() }));

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe('/acesso-negado');
  });

  it('redirects unauthenticated users to login', () => {
    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe('/login');
  });

  it('redirects users with an expired token to login', () => {
    localStorage.setItem('abaco_token', makeToken({ cargo: 1, exp: Math.floor(Date.now() / 1000) - 60 }));

    const guard = roleGuard([1, 3]);
    const result = TestBed.runInInjectionContext(() => guard({} as never, {} as never));

    expect(result).toBe('/login');
  });
});
