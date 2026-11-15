import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AuthService, getStoredSession, mapCargoToRole } from './auth.service';
import { fakeJwt } from '../testing/fake-jwt';

const SESSION_KEY = 'abaco_session';
const LOGIN_URL = 'http://localhost:8000/api/v1/auth/login';
const LOGOUT_URL = 'http://localhost:8000/api/v1/auth/logout';

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

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let router: { navigate: ReturnType<typeof vi.fn> };

  const loginResponse = {
    access_token: fakeJwt({ sub: '1', cargo: 1 }),
    token_type: 'bearer',
    usuario: {
      idUsuario: 1,
      nome: 'Admin',
      email: 'admin@abaco.org.br',
      cargo: 1,
      primeiro_acesso: false,
    },
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

  it('login guarda apenas metadados da sessão, nunca o JWT', () => {
    service.login('admin@abaco.org.br', 'senha').subscribe((res) => {
      expect(res.role).toBe('DIRECTOR');
    });

    const req = httpMock.expectOne(LOGIN_URL);
    expect(req.request.withCredentials).toBe(true);
    expect(req.request.body).toEqual({ email: 'admin@abaco.org.br', senha: 'senha' });
    req.flush(loginResponse);

    expect(localStorage.getItem('abaco_token')).toBeNull();
    expect(getStoredSession()).toMatchObject({
      userId: 1,
      cargo: 1,
      role: 'DIRECTOR',
      primeiroAcesso: false,
    });
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

  it('logout revoga a sessão no servidor e limpa os metadados locais', () => {
    storeSession();

    service.logout();

    const req = httpMock.expectOne(LOGOUT_URL);
    expect(req.request.method).toBe('POST');
    expect(req.request.withCredentials).toBe(true);
    req.flush(null, { status: 204, statusText: 'No Content' });

    expect(getStoredSession()).toBeNull();
    expect(service.authState().role).toBeNull();
  });

  it('logout limpa a sessão mesmo quando a revogação falha', () => {
    storeSession();

    service.logout();

    const req = httpMock.expectOne(LOGOUT_URL);
    req.flush({}, { status: 500, statusText: 'Server Error' });

    expect(getStoredSession()).toBeNull();
  });

  it('logoutAndRedirect limpa a sessão e navega sem chamar a API', () => {
    storeSession();
    service.logoutAndRedirect();

    expect(httpMock.match(LOGOUT_URL)).toHaveLength(0);
    expect(getStoredSession()).toBeNull();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('isAuthenticated returns false with no session', () => {
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
    });

    it('getRoleFromToken sem sessão -> GUEST', () => {
      expect(service.getRoleFromToken()).toBe('GUEST');
    });

    it('getRoleFromToken com sessão malformada -> GUEST (não lança)', () => {
      localStorage.setItem(SESSION_KEY, 'nao-e-json');
      expect(service.getRoleFromToken()).toBe('GUEST');
    });
  });

  describe('sessão, utilitários e erros de rede', () => {
    it('getUserId reflete o usuário da sessão restaurada', () => {
      storeSession({ userId: 42, cargo: 2, role: 'TEACHER' });
      (service as unknown as { restoreSession: () => void }).restoreSession();

      expect(service.getUserId()).toBe(42);
      service.logout();
      httpMock.match(LOGOUT_URL).forEach((req) => req.flush(null));
    });

    it('hasRole decide pela role da sessão', () => {
      storeSession({ cargo: 3, role: 'ADMIN' });
      expect(service.hasRole(['ADMIN'])).toBe(true);
      expect(service.hasRole(['DIRECTOR'])).toBe(false);
    });

    it('getCargo retorna o cargo da sessão', () => {
      storeSession({ cargo: 2, role: 'TEACHER' });
      expect(service.getCargo()).toBe(2);
    });

    it('isAuthenticated é true com sessão válida e false com expirada', () => {
      storeSession();
      expect(service.isAuthenticated()).toBe(true);

      storeSession({ expiresAt: Math.floor(Date.now() / 1000) - 60 });
      expect(service.isAuthenticated()).toBe(false);
    });

    it('restoreSession restaura sessão válida', () => {
      storeSession({ userId: 7, cargo: 2, role: 'TEACHER' });
      (service as unknown as { restoreSession: () => void }).restoreSession();

      expect(service.authState().role).toBe('TEACHER');
      expect(service.authState().userId).toBe(7);
      service.logout();
      httpMock.match(LOGOUT_URL).forEach((req) => req.flush(null));
    });

    it('restoreSession descarta sessão expirada', () => {
      storeSession({ expiresAt: Math.floor(Date.now() / 1000) - 60 });
      (service as unknown as { restoreSession: () => void }).restoreSession();

      expect(getStoredSession()).toBeNull();
    });

    it('agenda logout automático quando a sessão expira', () => {
      vi.useFakeTimers();
      try {
        (
          service as unknown as { scheduleAutoLogout: (expiresAt: number) => void }
        ).scheduleAutoLogout(Math.floor(Date.now() / 1000) + 3600);
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
      const req = httpMock.expectOne(LOGIN_URL);
      req.flush(
        { detail: 'E-mail ou senha incorretos' },
        { status: 401, statusText: 'Unauthorized' },
      );

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
      service
        .resetPassword('token', 'novaSenha1', 'novaSenha1')
        .subscribe({ error: (err) => (captured = err) });
      const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/reset-password');
      req.flush({}, { status: 400, statusText: 'Bad Request' });

      expect(captured?.status).toBe(400);
    });
  });
});
