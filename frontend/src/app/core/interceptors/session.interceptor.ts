import { HttpInterceptorFn } from '@angular/common/http';

import { environment } from '../../../environments/environment';

const CSRF_COOKIE_NAME = 'abaco_csrf';
const CSRF_HEADER_NAME = 'X-CSRF-Token';
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

function readCookie(name: string): string | null {
  const prefix = `${name}=`;
  const entry = document.cookie
    .split(';')
    .map((part) => part.trim())
    .find((part) => part.startsWith(prefix));
  return entry ? decodeURIComponent(entry.slice(prefix.length)) : null;
}

export const sessionInterceptor: HttpInterceptorFn = (req, next) => {
  const isApiRequest =
    req.url.startsWith(`${environment.apiUrl}/api/`) || req.url.startsWith('/api/');

  if (!isApiRequest) {
    return next(req);
  }

  const csrfToken = SAFE_METHODS.has(req.method) ? null : readCookie(CSRF_COOKIE_NAME);
  return next(
    req.clone({
      withCredentials: true,
      setHeaders: csrfToken ? { [CSRF_HEADER_NAME]: csrfToken } : {},
    }),
  );
};
