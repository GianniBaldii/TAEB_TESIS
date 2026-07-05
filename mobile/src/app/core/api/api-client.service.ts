import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiClientService {
  readonly baseUrl = environment.apiBaseUrl;

  constructor(readonly http: HttpClient) {}

  url(path: string): string {
    return `${this.baseUrl}${path}`;
  }
}
