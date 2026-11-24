import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { getStoredSession } from '../services/auth.service';
import { authGuard } from './auth.guard';

const SESSION_KEY = 'abaco_session';

function storeSession(overrides: Record<string, unknown> = {}): void {
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      userId: 1,
      cargo: 1,
      role: 'DIRECTOR',
      primeiroAcesso: false,
      expiresAt: Math.floor(Date.now() / 1000) + 3600,
      ...overrides,
    }),
  );
}

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
    storeSession({ cargo: null, role: 'GUEST' });
    expect(run()).toBe(true);
  });

  it('redireciona para /login sem sessão', () => {
    expect(run()).toBe('/login');
  });

  it('redireciona para /login com sessão expirada e limpa o storage', () => {
    storeSession({ expiresAt: Math.floor(Date.now() / 1000) - 60 });
    expect(run()).toBe('/login');
    expect(getStoredSession()).toBeNull();
  });

  it('redireciona para troca de senha quando o primeiro acesso está pendente', () => {
    storeSession({ primeiroAcesso: true });
    expect(
      TestBed.runInInjectionContext(() => authGuard({} as never, { url: '/admin' } as never)),
    ).toBe('/alterar-senha');
  });
});
