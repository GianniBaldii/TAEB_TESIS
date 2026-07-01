import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { AlumnoExam, AlumnoMe, AlumnoProfile } from '../models/alumno.models';
import { AlumnoProgress } from '../models/progreso.models';
import { ApiClientService } from './api-client.service';

@Injectable({ providedIn: 'root' })
export class AlumnoApiService {
  constructor(private api: ApiClientService) {}

  me(): Observable<AlumnoMe> {
    return this.api.http.get<AlumnoMe>(this.api.url('/me/'));
  }

  profile(): Observable<AlumnoProfile> {
    return this.api.http.get<AlumnoProfile>(this.api.url('/me/profile/'));
  }

  progress(): Observable<AlumnoProgress> {
    return this.api.http.get<AlumnoProgress>(this.api.url('/me/progress/'));
  }

  exams(): Observable<AlumnoExam[]> {
    return this.api.http.get<AlumnoExam[]>(this.api.url('/me/exams/'));
  }
}
