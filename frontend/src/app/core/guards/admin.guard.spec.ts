import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { adminGuard } from './role.guard';

const SESSION_KEY = 'abaco_session';

function storeSession(cargo: number | null): void {
  const role = cargo === 1 ? 'DIRECTOR' : cargo === 2 ? 'TEACHER' : cargo === 3 ? 'ADMIN' : 'GUEST';
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      userId: 1,
      cargo,
      role,
      primeiroAcesso: false,
      expiresAt: Math.floor(Date.now() / 1000) + 3600,
    }),
  );
}

describe('adminGuard (cargos 1 e 3)', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
    localStorage.clear();
  });

  afterEach(() => localStorage.clear());

  const run = () => TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));

  it('permite DIRECTOR (cargo 1)', () => {
    storeSession(1);
    expect(run()).toBe(true);
  });

  it('permite ADMIN (cargo 3)', () => {
    storeSession(3);
    expect(run()).toBe(true);
  });

  it('nega TEACHER (cargo 2)', () => {
    storeSession(2);
    expect(run()).toBe('/acesso-negado');
  });

  it('nega GUEST (cargo null)', () => {
    storeSession(null);
    expect(run()).toBe('/acesso-negado');
  });

  it('redireciona para /login sem sessão', () => {
    expect(run()).toBe('/login');
  });
});
