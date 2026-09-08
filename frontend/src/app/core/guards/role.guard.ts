import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { decodePayload, getStoredToken, isTokenExpired, clearStoredToken } from '../services/auth.service';

export function roleGuard(allowedCargos: number[]): CanActivateFn {
  return () => {
    const router = inject(Router);
    const token = getStoredToken();

    if (!token) {
      return router.parseUrl('/login');
    }

    if (isTokenExpired(token)) {
      clearStoredToken();
      return router.parseUrl('/login');
    }

    const payload = decodePayload(token);
    const cargo = payload.cargo ?? null;

    if (cargo === null || !allowedCargos.includes(cargo)) {
      return router.parseUrl('/acesso-negado');
    }

    return true;
  };
}

export const directorGuard = roleGuard([1]);
export const adminGuard = roleGuard([1, 3]);
