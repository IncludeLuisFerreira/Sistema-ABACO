import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, catchError, map, throwError, tap } from 'rxjs';

import { environment } from '../../../environments/environment';

interface LoginApiResponse {
  access_token: string;
  token_type: string;
  usuario: {
    idUsuario: number;
    nome: string | null;
    email: string;
    cargo: number | null;
    primeiro_acesso: boolean;
  };
}

export type AppRole = 'DIRECTOR' | 'ADMIN' | 'TEACHER' | 'GUEST';

export interface LoginResponse {
  token: string;
  role: AppRole;
  primeiroAcesso: boolean;
}

export interface JwtPayload {
  sub?: string;
  cargo?: number;
  primeiro_acesso?: boolean;
  exp?: number;
}

export interface StoredSession {
  userId: number | null;
  cargo: number | null;
  role: AppRole;
  primeiroAcesso: boolean;
  expiresAt: number;
}

const SESSION_STORAGE_KEY = 'abaco_session';
const SESSION_ROLES: AppRole[] = ['DIRECTOR', 'ADMIN', 'TEACHER', 'GUEST'];

export function decodePayload(token: string): JwtPayload {
  const parts = token.split('.');
  if (parts.length !== 3) {
    return {};
  }

  try {
    const normalized = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
    const decoded = atob(padded);
    return JSON.parse(decoded) as JwtPayload;
  } catch {
    return {};
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodePayload(token);
  if (!payload.exp) return true;

  const now = Math.floor(Date.now() / 1000);
  return payload.exp < now;
}

export function isSessionExpired(session: StoredSession): boolean {
  return session.expiresAt <= Math.floor(Date.now() / 1000);
}

export function getStoredSession(): StoredSession | null {
  const raw = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as Partial<StoredSession>;
    if (
      typeof parsed.expiresAt !== 'number' ||
      typeof parsed.primeiroAcesso !== 'boolean' ||
      !parsed.role ||
      !SESSION_ROLES.includes(parsed.role)
    ) {
      return null;
    }
    return {
      userId: typeof parsed.userId === 'number' ? parsed.userId : null,
      cargo: typeof parsed.cargo === 'number' ? parsed.cargo : null,
      role: parsed.role,
      primeiroAcesso: parsed.primeiroAcesso,
      expiresAt: parsed.expiresAt,
    };
  } catch {
    return null;
  }
}

export function clearStoredSession(): void {
  localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function mapCargoToRole(cargo: number | null | undefined): LoginResponse['role'] {
  if (cargo === 1) return 'DIRECTOR';
  if (cargo === 2) return 'TEACHER';
  if (cargo === 3) return 'ADMIN';
  // Cargo desconhecido vira guest sem permissão nenhuma
  return 'GUEST';
}

interface AuthState {
  userId: number | null;
  role: AppRole | null;
  expiresAt: number | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  // REFACTOR: auth usa URL absoluta; os demais serviços usam '/api' relativo
  private readonly loginUrl = `${environment.apiUrl}/api/v1/auth/login`;
  private readonly logoutUrl = `${environment.apiUrl}/api/v1/auth/logout`;
  private readonly forgotPasswordUrl = `${environment.apiUrl}/api/v1/auth/forgot-password`;
  private readonly resetPasswordUrl = `${environment.apiUrl}/api/v1/auth/reset-password`;
  private readonly firstAccessUrl = `${environment.apiUrl}/api/v1/auth/first-access`;
  private readonly changePasswordUrl = `${environment.apiUrl}/api/v1/auth/change-password`;

  readonly authState = signal<AuthState>({ userId: null, role: null, expiresAt: null });

  private tokenExpiryTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly router = inject(Router);

  constructor(private http: HttpClient) {
    this.restoreSession();
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginApiResponse>(this.loginUrl, { email, senha: password }, { withCredentials: true })
      .pipe(
        map((response) => {
          const payload = decodePayload(response.access_token);
          const role = mapCargoToRole(response.usuario.cargo);
          const session: StoredSession = {
            userId: response.usuario.idUsuario,
            cargo: response.usuario.cargo ?? null,
            role,
            primeiroAcesso: response.usuario.primeiro_acesso === true,
            expiresAt: payload.exp ?? Math.floor(Date.now() / 1000) + 3600,
          };
          return {
            token: response.access_token,
            role,
            primeiroAcesso: session.primeiroAcesso,
            session,
          };
        }),
        tap(({ session }) => this.persistSession(session)),
        map(({ token, role, primeiroAcesso }) => ({ token, role, primeiroAcesso })),
        catchError((error) => {
          const message = error?.error?.detail || error?.message || 'Credenciais inválidas';
          return throwError(() => ({ status: error?.status, message }));
        }),
      );
  }

  forgotPassword(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(this.forgotPasswordUrl, { email }).pipe(
      catchError((error) => {
        const message = error?.error?.detail || error?.message || 'Erro ao processar solicitação';
        return throwError(() => ({ status: error?.status, message }));
      }),
    );
  }

  resetPassword(
    token: string,
    nova_senha: string,
    confirmar_senha: string,
  ): Observable<{ message: string }> {
    return this.http
      .post<{ message: string }>(this.resetPasswordUrl, { token, nova_senha, confirmar_senha })
      .pipe(
        catchError((error) => {
          const message = error?.error?.detail || error?.message || 'Erro ao redefinir senha';
          return throwError(() => ({ status: error?.status, message }));
        }),
      );
  }

  firstAccess(
    token: string,
    nova_senha: string,
    confirmar_senha: string,
  ): Observable<{ message: string }> {
    return this.http
      .post<{ message: string }>(this.firstAccessUrl, { token, nova_senha, confirmar_senha })
      .pipe(
        catchError((error) => {
          const message = error?.error?.detail || error?.message || 'Erro ao definir senha';
          return throwError(() => ({ status: error?.status, message }));
        }),
      );
  }

  changePassword(
    senha_atual: string,
    nova_senha: string,
    confirmar_senha: string,
  ): Observable<{ message: string }> {
    return this.http
      .post<{
        message: string;
      }>(this.changePasswordUrl, { senha_atual, nova_senha, confirmar_senha })
      .pipe(
        catchError((error) => {
          const message = error?.error?.detail || error?.message || 'Erro ao alterar senha';
          return throwError(() => ({ status: error?.status, message }));
        }),
      );
  }

  isFirstAccessPending(): boolean {
    return getStoredSession()?.primeiroAcesso === true;
  }

  logout(): void {
    this.clearAutoLogout();
    this.revokeServerSession();
    this.clearSessionState();
  }

  logoutAndRedirect(): void {
    this.clearAutoLogout();
    this.clearSessionState();
    this.router.navigate(['/login']);
  }

  isAuthenticated(): boolean {
    const session = getStoredSession();
    if (!session) return false;
    return !isSessionExpired(session);
  }

  hasRole(allowedRoles: AppRole[]): boolean {
    return allowedRoles.includes(this.getRoleFromToken());
  }

  getUserId(): number | null {
    return this.authState().userId ?? getStoredSession()?.userId ?? null;
  }

  getCargo(): number | null {
    return getStoredSession()?.cargo ?? null;
  }

  getRoleFromToken(): LoginResponse['role'] {
    return getStoredSession()?.role ?? 'GUEST';
  }

  private persistSession(session: StoredSession): void {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
    this.authState.set({
      userId: session.userId,
      role: session.role,
      expiresAt: session.expiresAt,
    });
    this.scheduleAutoLogout(session.expiresAt);
  }

  private revokeServerSession(): void {
    // Requisição best-effort: o logout local nunca depende da rede.
    this.http.post(this.logoutUrl, {}, { withCredentials: true }).subscribe({
      error: () => undefined,
    });
  }

  private clearSessionState(): void {
    clearStoredSession();
    this.authState.set({ userId: null, role: null, expiresAt: null });
  }

  private scheduleAutoLogout(expiresAt: number): void {
    this.clearAutoLogout();
    const remainingMs = (expiresAt - Math.floor(Date.now() / 1000)) * 1000;
    if (remainingMs <= 0) {
      this.logoutAndRedirect();
      return;
    }

    this.tokenExpiryTimer = setTimeout(() => {
      this.logoutAndRedirect();
    }, remainingMs);
  }

  private clearAutoLogout(): void {
    if (this.tokenExpiryTimer !== null) {
      clearTimeout(this.tokenExpiryTimer);
      this.tokenExpiryTimer = null;
    }
  }

  private restoreSession(): void {
    const session = getStoredSession();
    if (!session) return;

    if (isSessionExpired(session)) {
      clearStoredSession();
      return;
    }

    this.authState.set({
      userId: session.userId,
      role: session.role,
      expiresAt: session.expiresAt,
    });
    this.scheduleAutoLogout(session.expiresAt);
  }
}
