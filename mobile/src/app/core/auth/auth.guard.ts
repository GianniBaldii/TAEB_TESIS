import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const access = await auth.getAccessToken();
  if (access) {
    return true;
  }
  return router.parseUrl('/auth/login');
};
