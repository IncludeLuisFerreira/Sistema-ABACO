import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { fakeJwt } from '../testing/fake-jwt';
import { adminGuard } from './role.guard';

const TOKEN_KEY = 'abaco_token';

describe('adminGuard (cargos 1 e 3)', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: Router, useValue: { parseUrl: (url: string) => url } }],
    });
    localStorage.clear();
  });

  afterEach(() => localStorage.clear());

  const run = () => TestBed.runInInjectionContext(() => adminGuard({} as never, {} as never));
  const withToken = (token: string) => localStorage.setItem(TOKEN_KEY, token);

  it('permite DIRECTOR (cargo 1)', () => {
    withToken(fakeJwt({ cargo: 1 }));
    expect(run()).toBe(true);
  });

  it('permite ADMIN (cargo 3)', () => {
    withToken(fakeJwt({ cargo: 3 }));
    expect(run()).toBe(true);
  });

  it('nega TEACHER (cargo 2)', () => {
    withToken(fakeJwt({ cargo: 2 }));
    expect(run()).toBe('/acesso-negado');
  });

  it('nega GUEST (cargo null)', () => {
    withToken(fakeJwt({ cargo: null }));
    expect(run()).toBe('/acesso-negado');
  });

  it('redireciona para /login sem token', () => {
    expect(run()).toBe('/login');
  });
});
