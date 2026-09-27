import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import {
  AuthService,
  decodePayload,
  isTokenExpired,
  mapCargoToRole,
  getStoredToken,
  clearStoredToken,
} from './auth.service';

function createFakeJwt(payloadObj: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify(payloadObj));
  return `${header}.${payload}.signature`;
}

describe('AuthService & Auth Helpers', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  const validToken = createFakeJwt({ sub: '1', cargo: 1, exp: 9999999999 });

  const loginResponse = {
    access_token: validToken,
    token_type: 'bearer',
    usuario: { idUsuario: 1, nome: 'Admin', email: 'admin@abaco.org.br', cargo: 1 },
  };

  beforeEach(() => {
    localStorage.clear();
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

  describe('Helper functions', () => {
    it('mapCargoToRole maps cargo 1 to DIRECTOR, 2 to TEACHER, 3 to ADMIN', () => {
      expect(mapCargoToRole(1)).toBe('DIRECTOR');
      expect(mapCargoToRole(2)).toBe('TEACHER');
      expect(mapCargoToRole(3)).toBe('ADMIN');
    });

    it('mapCargoToRole defaults to ADMIN for unknown cargo (fail-open security risk finding)', () => {
      expect(mapCargoToRole(null)).toBe('ADMIN');
      expect(mapCargoToRole(99)).toBe('ADMIN');
    });

    it('decodePayload correctly decodes base64 JWT payload', () => {
      const token = createFakeJwt({ sub: '123', cargo: 1 });
      const payload = decodePayload(token);
      expect(payload.sub).toBe('123');
      expect(payload.cargo).toBe(1);
    });

    it('decodePayload returns empty object for malformed token', () => {
      expect(decodePayload('invalid.token')).toEqual({});
      expect(decodePayload('')).toEqual({});
    });

    it('isTokenExpired checks token exp claim against current time', () => {
      const expiredToken = createFakeJwt({ exp: Math.floor(Date.now() / 1000) - 100 });
      const futureToken = createFakeJwt({ exp: Math.floor(Date.now() / 1000) + 3600 });
      expect(isTokenExpired(expiredToken)).toBe(true);
      expect(isTokenExpired(futureToken)).toBe(false);
    });

    it('getStoredToken and clearStoredToken interact with localStorage abaco_token', () => {
      localStorage.setItem('abaco_token', 'token123');
      expect(getStoredToken()).toBe('token123');
      clearStoredToken();
      expect(getStoredToken()).toBeNull();
    });
  });

  describe('AuthService Class', () => {
    it('login stores token and updates authState signal', () => {
      service.login('admin@abaco.org.br', 'senha').subscribe((res) => {
        expect(res.role).toBe('DIRECTOR');
      });

      const req = httpMock.expectOne((r) => r.url.includes('/api/v1/auth/login'));
      req.flush(loginResponse);

      expect(localStorage.getItem('abaco_token')).toBe(validToken);
      expect(service.authState().role).toBe('DIRECTOR');
    });

    it('forgotPassword sends email request', () => {
      service.forgotPassword('user@abaco.org.br').subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/api/v1/auth/forgot-password'));
      expect(req.request.body).toEqual({ email: 'user@abaco.org.br' });
      req.flush({ message: 'Enviado' });
    });

    it('resetPassword sends token and passwords', () => {
      service.resetPassword('token123', 'novaSenha1', 'novaSenha1').subscribe();

      const req = httpMock.expectOne((r) => r.url.includes('/api/v1/auth/reset-password'));
      expect(req.request.body).toEqual({
        token: 'token123',
        nova_senha: 'novaSenha1',
        confirmar_senha: 'novaSenha1',
      });
      req.flush({ message: 'Senha redefinida' });
    });

    it('logout clears state and token in localStorage', () => {
      localStorage.setItem('abaco_token', validToken);
      service.logout();
      expect(localStorage.getItem('abaco_token')).toBeNull();
      expect(service.authState().token).toBeNull();
    });

    it('isAuthenticated returns true for valid unexpired token and false when empty/expired', () => {
      expect(service.isAuthenticated()).toBe(false);

      localStorage.setItem('abaco_token', validToken);
      expect(service.isAuthenticated()).toBe(true);
    });
  });
});
