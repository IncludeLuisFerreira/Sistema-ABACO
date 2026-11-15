import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { getStoredSession } from '../services/auth.service';
import { roleGuard } from './role.guard';

const SESSION_KEY = 'abaco_session';

function storeSession(cargo: number | null, overrides: Record<string, unknown> = {}): void {
  const role = cargo === 1 ? 'DIRECTOR' : cargo === 2 ? 'TEACHER' : cargo === 3 ? 'ADMIN' : 'GUEST';
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      userId: 1,
      cargo,
      role,
      primeiroAcesso: false,
      expiresAt: Math.floor(Date.now() / 1000) + 3600,
      ...overrides,
    }),
  );
}

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

  it('permite DIRECTOR (cargo 1) na allowlist [1, 3]', () => {
    storeSession(1);
    expect(run([1, 3])).toBe(true);
  });

  it('permite ADMIN (cargo 3) na allowlist [1, 3]', () => {
    storeSession(3);
    expect(run([1, 3])).toBe(true);
  });

  it('nega TEACHER (cargo 2) na allowlist [1, 3]', () => {
    storeSession(2);
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega GUEST (cargo null) — o bug de fail-open corrigido', () => {
    storeSession(null);
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega cargo fora do enum (99)', () => {
    storeSession(99);
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega sessão sem cargo', () => {
    storeSession(null, { cargo: null });
    expect(run([1, 3])).toBe('/acesso-negado');
  });

  it('nega sessão malformada sem lançar exceção', () => {
    localStorage.setItem(SESSION_KEY, 'nao-e-json');
    expect(run([1, 3])).toBe('/login');
  });

  it('nega sessão expirada e limpa o storage', () => {
    storeSession(1, { expiresAt: Math.floor(Date.now() / 1000) - 60 });
    expect(run([1, 3])).toBe('/login');
    expect(getStoredSession()).toBeNull();
  });

  it('redireciona para /login quando não há sessão', () => {
    expect(run([1, 3])).toBe('/login');
  });
});
