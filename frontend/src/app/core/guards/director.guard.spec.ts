import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { directorGuard } from './role.guard';

function makeToken(payload: Record<string, unknown>): string {
  return `header.${btoa(JSON.stringify(payload))}.signature`;
}

function futureExp(): number {
  return Math.floor(Date.now() / 1000) + 3600;
}

describe('directorGuard', () => {
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
  });

  afterEach(() => localStorage.clear());

  it('allows access for director (cargo 1)', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '1', cargo: 1, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, { url: '/admin/usuarios' } as never));
    expect(result).toBe(true);
  });

  it('denies access for admin (cargo 3)', () => {
    localStorage.setItem('abaco_token', makeToken({ sub: '3', cargo: 3, exp: futureExp() }));

    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, { url: '/admin/usuarios' } as never));
    expect(result).toBe('/acesso-negado');
  });

  it('redirects when no token', () => {
    const result = TestBed.runInInjectionContext(() => directorGuard({} as never, { url: '/admin/usuarios' } as never));
    expect(result).toBe('/login');
  });
});
