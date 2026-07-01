import { Injectable } from '@angular/core';
import { Capacitor } from '@capacitor/core';
import { SecureStoragePlugin } from 'capacitor-secure-storage-plugin';

import { AuthTokens } from '../models/auth.models';

export interface TokenStorage {
  saveTokens(tokens: AuthTokens): Promise<void>;
  getAccessToken(): Promise<string | null>;
  getRefreshToken(): Promise<string | null>;
  clearTokens(): Promise<void>;
}

const ACCESS_KEY = 'taeb_access_token';
const REFRESH_KEY = 'taeb_refresh_token';

@Injectable({ providedIn: 'root' })
export class SecureStorageService implements TokenStorage {
  private memoryAccessToken: string | null = null;
  private memoryRefreshToken: string | null = null;

  async saveTokens(tokens: AuthTokens): Promise<void> {
    this.memoryAccessToken = tokens.access;
    this.memoryRefreshToken = tokens.refresh;
    await this.set(ACCESS_KEY, tokens.access);
    await this.set(REFRESH_KEY, tokens.refresh);
  }

  getAccessToken(): Promise<string | null> {
    return this.get(ACCESS_KEY);
  }

  getRefreshToken(): Promise<string | null> {
    return this.get(REFRESH_KEY);
  }

  async clearTokens(): Promise<void> {
    this.memoryAccessToken = null;
    this.memoryRefreshToken = null;
    await this.remove(ACCESS_KEY);
    await this.remove(REFRESH_KEY);
  }

  private async get(key: string): Promise<string | null> {
    if (!Capacitor.isNativePlatform()) {
      return key === ACCESS_KEY ? this.memoryAccessToken : this.memoryRefreshToken;
    }
    try {
      const result = await SecureStoragePlugin.get({ key });
      return result.value ?? null;
    } catch {
      return null;
    }
  }

  private async set(key: string, value: string): Promise<void> {
    if (!Capacitor.isNativePlatform()) {
      return;
    }
    await SecureStoragePlugin.set({ key, value });
  }

  private async remove(key: string): Promise<void> {
    if (!Capacitor.isNativePlatform()) {
      return;
    }
    try {
      await SecureStoragePlugin.remove({ key });
    } catch {
      return;
    }
  }
}
