import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { clearStoredToken, getStoredToken, isFirstAccessPending, isTokenExpired } from '../services/auth.service';

export const authGuard: CanActivateFn = (_route, state) => {
  const router = inject(Router);
  const token = getStoredToken();

  if (!token) {
    return router.parseUrl('/login');
  }

  if (isTokenExpired(token)) {
    clearStoredToken();
    return router.parseUrl('/login');
  }

  const targetUrl = state?.url ?? '';
  if (isFirstAccessPending(token) && !targetUrl.startsWith('/alterar-senha')) {
    return router.parseUrl('/alterar-senha');
  }

  return true;
};
