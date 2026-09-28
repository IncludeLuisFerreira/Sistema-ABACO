import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  const loginResponse = {
    access_token: 'header.eyJzdWIiOiIxIiwiY2FyZ28iOjEsImV4cCI6OTk5OTk5OTk5OX0.signature',
    token_type: 'bearer',
    usuario: { idUsuario: 1, nome: 'Admin', email: 'admin@abaco.org.br', cargo: 1, primeiro_acesso: false },
  };

  const firstAccessLoginResponse = {
    ...loginResponse,
    usuario: { ...loginResponse.usuario, primeiro_acesso: true },
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

  it('login exposes primeiroAcesso flag', () => {
    service.login('novo@abaco.org.br', 'senha').subscribe((res) => {
      expect(res.primeiroAcesso).toBe(true);
    });

    const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/login');
    req.flush(firstAccessLoginResponse);
  });

  it('firstAccess sends token and new password', () => {
    service.firstAccess('token123', 'novaSenha1', 'novaSenha1').subscribe();

    const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/first-access');
    expect(req.request.body).toEqual({
      token: 'token123',
      nova_senha: 'novaSenha1',
      confirmar_senha: 'novaSenha1',
    });
    req.flush({ message: 'Senha definida' });
  });

  it('changePassword sends current and new password', () => {
    service.changePassword('atual123', 'novaSenha1', 'novaSenha1').subscribe();

    const req = httpMock.expectOne('http://localhost:8000/api/v1/auth/change-password');
    expect(req.request.body).toEqual({
      senha_atual: 'atual123',
      nova_senha: 'novaSenha1',
      confirmar_senha: 'novaSenha1',
    });
    req.flush({ message: 'Senha alterada' });
  });

  it('isFirstAccessPending reads the flag from the stored token', () => {
    const token = `header.${btoa(JSON.stringify({ sub: '1', cargo: 2, primeiro_acesso: true, exp: 9999999999 }))}.signature`;
    localStorage.setItem('abaco_token', token);
    expect(service.isFirstAccessPending()).toBe(true);
  });
});
