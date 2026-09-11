import { HttpInterceptorFn } from '@angular/common/http';

export const tokenInterceptor: HttpInterceptorFn = (req, next) => {
  // FIXME: acessa localStorage direto e duplica a magic string 'abaco_token'
  const token = localStorage.getItem('abaco_token');

  if (!token) {
    return next(req);
  }

  return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
};
