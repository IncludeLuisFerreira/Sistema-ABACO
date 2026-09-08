import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);
  const auth = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        auth.logoutAndRedirect();
        return throwError(() => error);
      }

      if ([403, 409].includes(error.status)) {
        notifications.error(error.error?.detail || error.message || 'Erro ao processar a requisição.');
      }

      return throwError(() => error);
    })
  );
};