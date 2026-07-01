import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { AuthTokens, LoginPayload } from '../models/auth.models';
import { ApiClientService } from './api-client.service';

@Injectable({ providedIn: 'root' })
export class AuthApiService {
  constructor(private api: ApiClientService) {}

  login(payload: LoginPayload): Observable<AuthTokens> {
    return this.api.http.post<AuthTokens>(this.api.url('/auth/login/'), payload);
  }

  refresh(refresh: string): Observable<AuthTokens> {
    return this.api.http.post<AuthTokens>(this.api.url('/auth/refresh/'), { refresh });
  }

  logout(refresh: string): Observable<void> {
    return this.api.http.post<void>(this.api.url('/auth/logout/'), { refresh });
  }
}
