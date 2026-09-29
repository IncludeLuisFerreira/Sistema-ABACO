import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AuthService, isTokenExpired, mapCargoToRole } from './auth.service';
import { fakeExpiredJwt, fakeJwt } from '../testing/fake-jwt';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let router: { navigate: ReturnType<typeof vi.fn> };

  const loginResponse = {
    access_token: 'header.eyJzdWIiOiIxIiwiY2FyZ28iOjEsImV4cCI6OTk5OTk5OTk5OX0.signature',
    token_type: 'bearer',
    usuario: { idUsuario: 1, nome: 'Admin', email: 'admin@abaco.org.br', cargo: 1 },
  };

  beforeEach(() => {
    router = { navigate: vi.fn() };
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Router, useValue: router },
      ],
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

  describe('sessão, utilitários e erros de rede', () => {
    const TOKEN_KEY = 'abaco_token';

    it('setToken e getToken manipulam o storage', () => {
      service.setToken('abc.def.ghi');
      expect(localStorage.getItem(TOKEN_KEY)).toBe('abc.def.ghi');
      expect(service.getToken()).toBe('abc.def.ghi');
    });

    it('getUserId reflete o sub do token restaurado', () => {
      localStorage.setItem(TOKEN_KEY, fakeJwt({ sub: '42', cargo: 2 }));
      (service as unknown as { restoreSession: () => void }).restoreSession();
      expect(service.getUserId()).toBe(42);
      service.logout();
    });

    it('hasRole decide pela role derivada do cargo', () => {
      localStorage.setItem(TOKEN_KEY, fakeJwt({ cargo: 3 }));
      expect(service.hasRole(['ADMIN'])).toBe(true);
      expect(service.hasRole(['DIRECTOR'])).toBe(false);
    });

    it('isAuthenticated é true com token válido e false com expirado', () => {
      localStorage.setItem(TOKEN_KEY, fakeJwt({ cargo: 1 }));
      expect(service.isAuthenticated()).toBe(true);

      localStorage.setItem(TOKEN_KEY, fakeExpiredJwt({ cargo: 1 }));
      expect(service.isAuthenticated()).toBe(false);
    });

    it('isTokenExpired considera token sem exp como expirado', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const body = btoa(JSON.stringify({ sub: '1' }));
      expect(isTokenExpired(`${header}.${body}.assinatura`)).toBe(true);
    });

    it('restoreSession restaura sessão de token válido', () => {
      localStorage.setItem(TOKEN_KEY, fakeJwt({ sub: '7', cargo: 2 }));
      (service as unknown as { restoreSession: () => void }).restoreSession();
      expect(service.authState().role).toBe('TEACHER');
      expect(service.authState().token).not.toBeNull();
      service.logout();
    });

    it('restoreSession descarta token expirado', () => {
      localStorage.setItem(TOKEN_KEY, fakeExpiredJwt({ cargo: 1 }));
      (service as unknown as { restoreSession: () => void }).restoreSession();
      expect(service.getToken()).toBeNull();
    });

    it('logoutAndRedirect limpa a sessão e navega para /login', () => {
      service.setToken('abc.def.ghi');
      service.logoutAndRedirect();
      expect(service.getToken()).toBeNull();
      expect(router.navigate).toHaveBeenCalledWith(['/login']);
    });

    it('agenda logout automático quando o token expira', () => {
      vi.useFakeTimers();
      try {
        (service as unknown as { scheduleAutoLogout: (t: string) => void }).scheduleAutoLogout(
          fakeJwt({ cargo: 1 }),
        );
        vi.advanceTimersByTime(3600 * 1000 + 1000);
        expect(router.navigate).toHaveBeenCalledWith(['/login']);
      } finally {
        vi.useRealTimers();
      }
    });

    it('login propaga erro com detail do backend', () => {
      let captured: { status?: number; message?: string } | undefined;
      service.login('admin@abaco.org.br', 'x').subscribe({
        error: (err) => (captured = err),
      });
      const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/login');
      req.flush({ detail: 'E-mail ou senha incorretos' }, { status: 401, statusText: 'Unauthorized' });

      expect(captured?.status).toBe(401);
      expect(captured?.message).toBe('E-mail ou senha incorretos');
    });

    it('forgotPassword propaga erro de rede', () => {
      let captured: { status?: number } | undefined;
      service.forgotPassword('admin@abaco.org.br').subscribe({ error: (err) => (captured = err) });
      const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/forgot-password');
      req.flush({}, { status: 500, statusText: 'Server Error' });

      expect(captured?.status).toBe(500);
    });

    it('resetPassword propaga erro de rede', () => {
      let captured: { status?: number } | undefined;
      service.resetPassword('token', 'novaSenha1', 'novaSenha1').subscribe({ error: (err) => (captured = err) });
      const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/reset-password');
      req.flush({}, { status: 400, statusText: 'Bad Request' });

      expect(captured?.status).toBe(400);
    });
  });
});
