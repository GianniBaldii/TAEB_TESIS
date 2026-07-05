import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  IonCard,
  IonCardContent,
  IonChip,
  IonContent,
  IonHeader,
  IonIcon,
  IonTitle,
  IonToolbar
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { businessOutline, ribbonOutline, schoolOutline } from 'ionicons/icons';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-home',
  imports: [AsyncPipe, IonCard, IonCardContent, IonChip, IonContent, IonHeader, IonIcon, IonTitle, IonToolbar],
  template: `
    <ion-header>
      <ion-toolbar>
        <ion-title>
          <span class="toolbar-brand">
            <img src="assets/taeb-logo.svg" alt="TAEB">
          </span>
        </ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="page-shell home-shell">
        @if (me$ | async; as me) {
          <section class="hero-card">
            <div class="hero-copy">
              <p class="eyebrow">Bienvenido</p>
              <h1>{{ me.nombre_completo }}</h1>
              <p>Tu recorrido marcial, escuelas activas y estado de formación en un solo lugar.</p>
            </div>
            <img class="hero-logo" src="assets/taeb-logo.svg" alt="TAEB">
          </section>

          <section class="metric-grid">
            <div class="metric-card">
              <ion-icon name="ribbon-outline"></ion-icon>
              <strong>{{ me.cinturon_actual?.nombre || '-' }}</strong>
              <span>Cinturón actual</span>
            </div>
            <div class="metric-card">
              <ion-icon name="business-outline"></ion-icon>
              <strong>{{ me.escuelas_activas.length }}</strong>
              <span>Escuelas activas</span>
            </div>
          </section>

          <section class="section-block">
            <h2 class="section-title">Tus escuelas</h2>
            <ion-card class="school-card">
              <ion-card-content>
                @for (escuela of me.escuelas_activas; track escuela.id) {
                  <ion-chip>
                    <ion-icon name="school-outline"></ion-icon>
                    {{ escuela.nombre }}
                  </ion-chip>
                } @empty {
                  <div class="empty-state">
                    <ion-icon name="school-outline"></ion-icon>
                    <span>No hay escuelas activas asociadas a tu usuario.</span>
                  </div>
                }
              </ion-card-content>
            </ion-card>
          </section>
        }
      </div>
    </ion-content>
  `,
  styles: [`
    .toolbar-brand {
      align-items: center;
      display: inline-flex;
      height: 36px;
    }

    .toolbar-brand img {
      display: block;
      height: auto;
      max-height: 28px;
      object-fit: contain;
      width: 92px;
    }

    .home-shell {
      gap: 16px;
    }

    .hero-card {
      align-items: center;
      background: #172033;
      border-radius: 8px;
      color: #ffffff;
      display: grid;
      gap: 18px;
      grid-template-columns: minmax(0, 1fr) auto;
      overflow: hidden;
      padding: 20px;
      position: relative;
    }

    .hero-copy {
      min-width: 0;
      position: relative;
      z-index: 1;
    }

    .hero-card .eyebrow {
      color: rgba(255, 255, 255, 0.72);
    }

    .hero-card h1 {
      font-size: 25px;
      font-weight: 850;
      line-height: 1.08;
      margin: 0 0 8px;
      overflow-wrap: anywhere;
    }

    .hero-card p:not(.eyebrow) {
      color: rgba(255, 255, 255, 0.76);
      line-height: 1.4;
      margin: 0;
    }

    .hero-logo {
      background: rgba(255, 255, 255, 0.94);
      border-radius: 8px;
      box-shadow: 0 14px 28px rgba(0, 0, 0, 0.16);
      display: block;
      height: auto;
      object-fit: contain;
      padding: 8px;
      width: 112px;
    }

    .metric-card {
      min-height: 108px;
    }

    .metric-card ion-icon {
      color: var(--ion-color-primary);
      font-size: 22px;
      margin-bottom: 12px;
    }

    .metric-card strong {
      overflow-wrap: anywhere;
    }

    .section-block {
      display: grid;
      gap: 10px;
    }

    .school-card {
      margin: 0;
    }

    ion-chip {
      --background: #eef4ff;
      --color: #1d4ed8;
      border-radius: 8px;
      margin: 4px 6px 4px 0;
    }

    @media (max-width: 420px) {
      .hero-card {
        align-items: start;
        grid-template-columns: 1fr;
        padding: 18px;
      }

      .hero-logo {
        justify-self: start;
        margin-top: 2px;
        width: 126px;
      }
    }
  `]
})
export class HomePage {
  private alumnoApi = inject(AlumnoApiService);
  me$ = this.alumnoApi.me();

  constructor() {
    addIcons({ ribbonOutline, businessOutline, schoolOutline });
  }
}
