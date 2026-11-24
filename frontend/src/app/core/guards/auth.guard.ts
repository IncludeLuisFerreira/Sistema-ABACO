import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { clearStoredSession, getStoredSession, isSessionExpired } from '../services/auth.service';

export const authGuard: CanActivateFn = (_route, state) => {
  const router = inject(Router);
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

  return true;
};
