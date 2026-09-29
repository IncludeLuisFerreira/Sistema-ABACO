import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { adminGuard } from './role.guard';

function makeToken(payload: Record<string, unknown>): string {
  return `header.${btoa(JSON.stringify(payload))}.signature`;
}

function futureExp(): number {
  return Math.floor(Date.now() / 1000) + 3600;
}

describe('adminGuard', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
  });

  afterEach(() => localStorage.clear());

  it('allows access for admin (cargo 3)', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '3', cargo: 3, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, { url: '/admin/home' } as never));
    expect(result).toBe(true);
  });

  it('redirects when no token', () => {
    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, { url: '/admin/home' } as never));
    expect(result).toBe('/login');
  });

  it('denies access for teacher (cargo 2)', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '2', cargo: 2, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() => adminGuard({} as never, { url: '/admin/home' } as never));
    expect(result).toBe('/acesso-negado');
  });
});
