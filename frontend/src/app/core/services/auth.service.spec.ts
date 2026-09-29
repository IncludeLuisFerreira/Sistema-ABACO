import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { AuthService, mapCargoToRole } from './auth.service';
import { fakeJwt } from '../testing/fake-jwt';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  const loginResponse = {
    access_token: 'header.eyJzdWIiOiIxIiwiY2FyZ28iOjEsImV4cCI6OTk5OTk5OTk5OX0.signature',
    token_type: 'bearer',
    usuario: { idUsuario: 1, nome: 'Admin', email: 'admin@abaco.org.br', cargo: 1 },
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('login stores token and updates authState', () => {
    service.login('admin@abaco.org.br', 'senha').subscribe((res) => {
      expect(res.role).toBe('DIRECTOR');
    });

    const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/login');
    req.flush(loginResponse);

    expect(localStorage.getItem('abaco_token')).toBe(loginResponse.access_token);
    expect(service.authState().role).toBe('DIRECTOR');
  });

  it('forgotPassword sends email', () => {
    service.forgotPassword('user@abaco.org.br').subscribe();

    const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/forgot-password');
    expect(req.request.body).toEqual({ email: 'user@abaco.org.br' });
    req.flush({ message: 'Enviado' });
  });

  it('resetPassword sends token and new password', () => {
    service.resetPassword('token123', 'novaSenha1', 'novaSenha1').subscribe();

    const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/reset-password');
    expect(req.request.body).toEqual({
      token: 'token123',
      nova_senha: 'novaSenha1',
      confirmar_senha: 'novaSenha1',
    });
    req.flush({ message: 'Senha redefinida' });
  });

  it('logout clears state', () => {
    service.logout();
    expect(localStorage.getItem('abaco_token')).toBeNull();
    expect(service.authState().token).toBeNull();
  });

  it('isAuthenticated returns false with no token', () => {
    expect(service.isAuthenticated()).toBe(false);
  });

  describe('fail-closed no mapeamento de cargo', () => {
    const casos: Array<[number | null | undefined, string]> = [
      [1, 'DIRECTOR'],
      [2, 'TEACHER'],
      [3, 'ADMIN'],
      [null, 'GUEST'],
      [undefined, 'GUEST'],
      [0, 'GUEST'],
      [4, 'GUEST'],
      [-1, 'GUEST'],
      [99, 'GUEST'],
    ];

    casos.forEach(([cargo, esperado]) => {
      it(`mapCargoToRole(${JSON.stringify(cargo)}) -> ${esperado}`, () => {
        expect(mapCargoToRole(cargo)).toBe(esperado);
      });

      it(`getRoleFromToken com cargo ${JSON.stringify(cargo)} -> ${esperado}`, () => {
        localStorage.setItem('abaco_token', fakeJwt({ cargo }));
        expect(service.getRoleFromToken()).toBe(esperado);
      });
    });

    it('getRoleFromToken sem token -> GUEST', () => {
      localStorage.removeItem('abaco_token');
      expect(service.getRoleFromToken()).toBe('GUEST');
    });

    it('getRoleFromToken com token malformado -> GUEST (não lança)', () => {
      localStorage.setItem('abaco_token', 'nao-e-um-jwt');
      expect(service.getRoleFromToken()).toBe('GUEST');
    });

    it('getRoleFromToken com payload sem cargo -> GUEST', () => {
      localStorage.setItem('abaco_token', fakeJwt({ sub: 'u1' }));
      expect(service.getRoleFromToken()).toBe('GUEST');
    });
  });
});
