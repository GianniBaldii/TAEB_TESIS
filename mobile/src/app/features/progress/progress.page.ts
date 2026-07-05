import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  IonCard,
  IonCardContent,
  IonContent,
  IonHeader,
  IonIcon,
  IonProgressBar,
  IonTitle,
  IonToolbar
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { medalOutline, pulseOutline, timeOutline, trendingUpOutline } from 'ionicons/icons';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-progress',
  imports: [AsyncPipe, IonCard, IonCardContent, IonContent, IonHeader, IonIcon, IonProgressBar, IonTitle, IonToolbar],
  template: `
    <ion-header>
      <ion-toolbar>
        <ion-title>Progreso</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="page-shell">
        @if (progress$ | async; as progress) {
          <ion-card class="progress-card">
            <ion-card-content>
              <div class="progress-heading">
                <div>
                  <p class="eyebrow">Próximo objetivo</p>
                  <h1>{{ progress.proximo_cinturon?.nombre || 'Sin objetivo asignado' }}</h1>
                </div>
                <strong>{{ progress.estado_orientativo.porcentaje }}%</strong>
              </div>
              <ion-progress-bar [value]="progress.estado_orientativo.porcentaje / 100"></ion-progress-bar>
              <p class="status">{{ progress.estado_orientativo.mensaje }}</p>
            </ion-card-content>
          </ion-card>

          <section class="metric-grid">
            <div class="metric-card">
              <ion-icon name="medal-outline"></ion-icon>
              <strong>{{ progress.cinturon_actual?.nombre || '-' }}</strong>
              <span>Cinturón actual</span>
            </div>
            <div class="metric-card">
              <ion-icon name="time-outline"></ion-icon>
              <strong>{{ progress.tiempo_desde_ultimo_cinturon || '-' }}</strong>
              <span>Desde el último cambio</span>
            </div>
            <div class="metric-card">
              <ion-icon name="trending-up-outline"></ion-icon>
              <strong>{{ progress.examenes_aprobados }}</strong>
              <span>Exámenes aprobados</span>
            </div>
            <div class="metric-card">
              <ion-icon name="pulse-outline"></ion-icon>
              <strong>{{ progress.promociones_obtenidas }}</strong>
              <span>Promociones</span>
            </div>
          </section>

          <ion-card class="message-card">
            <ion-card-content>
              <p class="eyebrow">Estado orientativo</p>
              <h2>{{ progress.estado_orientativo.label }}</h2>
              <p>{{ progress.tiempo_orientativo }}</p>
            </ion-card-content>
          </ion-card>
        }
      </div>
    </ion-content>
  `,
  styles: [`
    .progress-card {
      background: #ffffff;
      margin: 0;
    }

    .progress-heading {
      align-items: start;
      display: flex;
      gap: 16px;
      justify-content: space-between;
      margin-bottom: 18px;
    }

    h1 {
      font-size: 24px;
      font-weight: 850;
      line-height: 1.08;
      margin: 0;
    }

    .progress-heading strong {
      color: var(--ion-color-primary);
      font-size: 24px;
    }

    ion-progress-bar {
      height: 10px;
      border-radius: 999px;
      overflow: hidden;
    }

    .status {
      color: #4b5872;
      margin: 14px 0 0;
    }

    .metric-card ion-icon {
      color: var(--ion-color-secondary);
      font-size: 22px;
      margin-bottom: 12px;
    }

    .metric-card strong {
      font-size: 20px;
      line-height: 1.1;
    }

    .message-card {
      margin: 0;
    }

    .message-card h2 {
      font-size: 18px;
      margin: 0 0 8px;
    }

    .message-card p:last-child {
      color: #4b5872;
      margin: 0;
    }
  `]
})
export class ProgressPage {
  private alumnoApi = inject(AlumnoApiService);
  progress$ = this.alumnoApi.progress();

  constructor() {
    addIcons({ medalOutline, timeOutline, trendingUpOutline, pulseOutline });
  }
}
