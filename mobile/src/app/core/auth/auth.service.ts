import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { AuthApiService } from '../api/auth-api.service';
import { LoginPayload } from '../models/auth.models';
import { SecureStorageService } from '../services/secure-storage.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(
    private authApi: AuthApiService,
    private storage: SecureStorageService,
    private router: Router
  ) {}

  async login(payload: LoginPayload): Promise<void> {
    const tokens = await firstValueFrom(this.authApi.login(payload));
    await this.storage.saveTokens(tokens);
  }

  async logout(): Promise<void> {
    const refresh = await this.storage.getRefreshToken();
    if (refresh) {
      try {
        await firstValueFrom(this.authApi.logout(refresh));
      } catch {
        // El cierre local sigue siendo obligatorio aunque el refresh ya no sea valido.
      }
    }
    await this.storage.clearTokens();
    await this.router.navigateByUrl('/auth/login', { replaceUrl: true });
  }

  getAccessToken(): Promise<string | null> {
    return this.storage.getAccessToken();
  }

  getRefreshToken(): Promise<string | null> {
    return this.storage.getRefreshToken();
  }

  clearTokens(): Promise<void> {
    return this.storage.clearTokens();
  }
}
