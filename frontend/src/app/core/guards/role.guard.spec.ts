import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { getStoredToken } from '../services/auth.service';
import { fakeExpiredJwt, fakeJwt } from '../testing/fake-jwt';
import { roleGuard } from './role.guard';

const TOKEN_KEY = 'abaco_token';

describe('roleGuard (fail-closed por cargo)', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  const run = (allowedCargos: number[]) =>
    TestBed.runInInjectionContext(() => roleGuard(allowedCargos)({} as never, {} as never));

  const withToken = (token: string) => localStorage.setItem(TOKEN_KEY, token);

  it('permite DIRECTOR (cargo 1) na allowlist [1, 3]', () => {
    withToken(fakeJwt({ cargo: 1 }));
    expect(run([1, 3])).toBe(true);
  });

  it('permite ADMIN (cargo 3) na allowlist [1, 3]', () => {
    withToken(fakeJwt({ cargo: 3 }));
    expect(run([1, 3])).toBe(true);
  });

  it('nega TEACHER (cargo 2) na allowlist [1, 3]', () => {
    withToken(fakeJwt({ cargo: 2 }));
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega GUEST (cargo null) — o bug de fail-open corrigido', () => {
    withToken(fakeJwt({ cargo: null }));
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega GUEST (cargo 0, falsy) — pega truthy-check acidental', () => {
    withToken(fakeJwt({ cargo: 0 }));
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega cargo fora do enum (99)', () => {
    withToken(fakeJwt({ cargo: 99 }));
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega payload sem campo cargo', () => {
    withToken(fakeJwt({ sub: 'u1' }));
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega token malformado sem lançar exceção', () => {
    withToken('nao-e-um-jwt');
    expect(run([1, 3])).toBe('/login');
  });

  it('nega token expirado e limpa o storage', () => {
    withToken(fakeExpiredJwt({ cargo: 1 }));
    expect(run([1, 3])).toBe('/login');
    expect(getStoredToken()).toBeNull();
  });

  it('redireciona para /login quando não há token', () => {
    expect(run([1, 3])).toBe('/login');
  });
});
