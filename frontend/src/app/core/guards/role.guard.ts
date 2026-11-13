import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { clearStoredSession, getStoredSession, isSessionExpired } from '../services/auth.service';

export function roleGuard(allowedCargos: number[]): CanActivateFn {
  return (_route, state) => {
    const router = inject(Router);
    // REFACTOR: duplica a verificação de sessão/expirada já feita no authGuard
    const session = getStoredSession();

    if (!session) {
      return router.parseUrl('/login');
    }

    if (isSessionExpired(session)) {
      clearStoredSession();
      return router.parseUrl('/login');
    }

    const targetUrl = state?.url ?? '';
    if (session.primeiroAcesso && !targetUrl.startsWith('/alterar-senha')) {
      return router.parseUrl('/alterar-senha');
    }

    const cargo = session.cargo;

    if (cargo === null || !allowedCargos.includes(cargo)) {
      return router.parseUrl('/acesso-negado');
    }

    return true;
  };
}

export const adminGuard = roleGuard([1, 3]);
