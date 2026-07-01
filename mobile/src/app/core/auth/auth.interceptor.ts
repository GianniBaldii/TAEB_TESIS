import { HttpInterceptorFn } from '@angular/common/http';
import { from, switchMap } from 'rxjs';

import { inject } from '@angular/core';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  if (req.url.includes('/auth/login/') || req.url.includes('/auth/refresh/')) {
    return next(req);
  }
  return from(auth.getAccessToken()).pipe(
    switchMap((token) => {
      if (!token) {
        return next(req);
      }
      return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
    })
  );
};
