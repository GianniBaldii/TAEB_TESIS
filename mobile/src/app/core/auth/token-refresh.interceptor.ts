import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, from, switchMap, throwError } from 'rxjs';

import { AuthApiService } from '../api/auth-api.service';
import { SecureStorageService } from '../services/secure-storage.service';

export const tokenRefreshInterceptor: HttpInterceptorFn = (req, next) => {
  const authApi = inject(AuthApiService);
  const storage = inject(SecureStorageService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      const puedeRefrescar =
        error.status === 401 &&
        !req.url.includes('/auth/login/') &&
        !req.url.includes('/auth/refresh/') &&
        !req.headers.has('X-TAEB-Retry');
      if (!puedeRefrescar) {
        return throwError(() => error);
      }
      return from(storage.getRefreshToken()).pipe(
        switchMap((refresh) => {
          if (!refresh) {
            throw error;
          }
          return authApi.refresh(refresh);
        }),
        switchMap((tokens) =>
          from(storage.saveTokens(tokens)).pipe(
            switchMap(() =>
              next(
                req.clone({
                  setHeaders: {
                    Authorization: `Bearer ${tokens.access}`,
                    'X-TAEB-Retry': '1'
                  }
                })
              )
            )
          )
        ),
        catchError(async () => {
          await storage.clearTokens();
          await router.navigateByUrl('/auth/login', { replaceUrl: true });
          throw error;
        })
      );
    })
  );
};
