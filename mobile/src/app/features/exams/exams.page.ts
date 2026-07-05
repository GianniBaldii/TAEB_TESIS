import { AsyncPipe, DatePipe, TitleCasePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  IonBadge,
  IonCard,
  IonCardContent,
  IonContent,
  IonHeader,
  IonIcon,
  IonTitle,
  IonToolbar
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { calendarClearOutline, checkmarkCircleOutline, clipboardOutline, locationOutline } from 'ionicons/icons';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-exams',
  imports: [AsyncPipe, DatePipe, TitleCasePipe, IonBadge, IonCard, IonCardContent, IonContent, IonHeader, IonIcon, IonTitle, IonToolbar],
  template: `
    <ion-header>
      <ion-toolbar>
        <ion-title>Exámenes</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="page-shell">
        @for (exam of exams$ | async; track exam.id) {
          <ion-card class="exam-card">
            <ion-card-content>
              <div class="exam-topline">
                <div class="date-block">
                  <ion-icon name="calendar-clear-outline"></ion-icon>
                  <span>{{ exam.fecha_examen | date:'dd/MM/yyyy' }}</span>
                </div>
                <ion-badge [color]="badgeColor(exam.estado)">{{ exam.estado | titlecase }}</ion-badge>
              </div>

              <h2>{{ exam.cinturon_destino?.nombre || 'Cinturón a confirmar' }}</h2>
              <p class="route">
                {{ exam.cinturon_origen?.nombre || '-' }} → {{ exam.cinturon_destino?.nombre || '-' }}
              </p>

              <div class="exam-meta">
                <span>
                  <ion-icon name="location-outline"></ion-icon>
                  {{ exam.lugar || 'Lugar a confirmar' }}
                </span>
                <span>
                  <ion-icon name="checkmark-circle-outline"></ion-icon>
                  Nota {{ exam.nota_final || '-' }}
                </span>
              </div>
            </ion-card-content>
          </ion-card>
        } @empty {
          <div class="empty-state">
            <ion-icon name="clipboard-outline"></ion-icon>
            <strong>No hay exámenes para mostrar</strong>
            <span>Cuando tengas un examen registrado, aparecerá en este listado.</span>
          </div>
        }
      </div>
    </ion-content>
  `,
  styles: [`
    .exam-card {
      margin: 0;
    }

    .exam-topline,
    .exam-meta,
    .date-block {
      align-items: center;
      display: flex;
    }

    .exam-topline {
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }

    .date-block {
      color: var(--ion-color-medium);
      gap: 7px;
      font-size: 13px;
      font-weight: 700;
    }

    h2 {
      font-size: 20px;
      font-weight: 850;
      margin: 0 0 6px;
    }

    .route {
      color: #4b5872;
      margin: 0 0 16px;
    }

    .exam-meta {
      color: var(--ion-color-medium);
      flex-wrap: wrap;
      gap: 10px 14px;
      font-size: 13px;
    }

    .exam-meta span {
      align-items: center;
      display: flex;
      gap: 5px;
    }

    ion-icon {
      color: var(--ion-color-primary);
    }
  `]
})
export class ExamsPage {
  private alumnoApi = inject(AlumnoApiService);
  exams$ = this.alumnoApi.exams();

  constructor() {
    addIcons({ calendarClearOutline, locationOutline, checkmarkCircleOutline, clipboardOutline });
  }

  badgeColor(estado: string): string {
    const normalized = estado.toLowerCase();

    if (normalized.includes('aprob')) {
      return 'success';
    }

    if (normalized.includes('pend') || normalized.includes('program')) {
      return 'warning';
    }

    return 'medium';
  }
}
