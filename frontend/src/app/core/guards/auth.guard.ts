import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { clearStoredToken, getStoredToken, isTokenExpired } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);
  const token = getStoredToken();

  if (!token) {
    return router.parseUrl('/login');
  }

  if (isTokenExpired(token)) {
    clearStoredToken();
    return router.parseUrl('/login');
  }

  return true;
};
