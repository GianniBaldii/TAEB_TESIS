import { AsyncPipe, DatePipe } from '@angular/common';
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
import { callOutline, idCardOutline, mailOutline, ribbonOutline, schoolOutline, todayOutline } from 'ionicons/icons';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-profile',
  imports: [AsyncPipe, DatePipe, IonCard, IonCardContent, IonChip, IonContent, IonHeader, IonIcon, IonTitle, IonToolbar],
  template: `
    <ion-header>
      <ion-toolbar>
        <ion-title>Perfil</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="page-shell">
        @if (profile$ | async; as profile) {
          <section class="profile-hero">
            <div class="avatar">{{ initials(profile.nombre, profile.apellido) }}</div>
            <div>
              <p class="eyebrow">Alumno</p>
              <h1>{{ profile.apellido }}, {{ profile.nombre }}</h1>
              <p>DNI {{ profile.dni }}</p>
            </div>
          </section>

          <section class="info-list">
            <ion-card>
              <ion-card-content>
                <ion-icon name="ribbon-outline"></ion-icon>
                <div>
                  <strong>{{ profile.cinturon_actual?.nombre || '-' }}</strong>
                  <span>Cinturón actual</span>
                </div>
              </ion-card-content>
            </ion-card>

            <ion-card>
              <ion-card-content>
                <ion-icon name="today-outline"></ion-icon>
                <div>
                  <strong>{{ profile.fecha_nacimiento ? (profile.fecha_nacimiento | date:'dd/MM/yyyy') : '-' }}</strong>
                  <span>Fecha de nacimiento</span>
                </div>
              </ion-card-content>
            </ion-card>

            <ion-card>
              <ion-card-content>
                <ion-icon name="mail-outline"></ion-icon>
                <div>
                  <strong>{{ profile.email || '-' }}</strong>
                  <span>Email</span>
                </div>
              </ion-card-content>
            </ion-card>

            <ion-card>
              <ion-card-content>
                <ion-icon name="call-outline"></ion-icon>
                <div>
                  <strong>{{ profile.telefono || '-' }}</strong>
                  <span>Teléfono</span>
                </div>
              </ion-card-content>
            </ion-card>
          </section>

          <h2 class="section-title">Escuelas</h2>
          <ion-card class="school-card">
            <ion-card-content>
              @for (escuela of profile.escuelas_activas; track escuela.id) {
                <ion-chip>
                  <ion-icon name="school-outline"></ion-icon>
                  {{ escuela.nombre }}
                </ion-chip>
              } @empty {
                <div class="empty-state">
                  <ion-icon name="id-card-outline"></ion-icon>
                  <span>No hay escuelas asociadas a tu perfil.</span>
                </div>
              }
            </ion-card-content>
          </ion-card>
        }
      </div>
    </ion-content>
  `,
  styles: [`
    .profile-hero {
      align-items: center;
      background: #ffffff;
      border: 1px solid rgba(23, 32, 51, 0.08);
      border-radius: 8px;
      display: grid;
      gap: 14px;
      grid-template-columns: auto 1fr;
      padding: 18px;
    }

    .avatar {
      align-items: center;
      background: #eef4ff;
      border-radius: 8px;
      color: var(--ion-color-primary);
      display: flex;
      font-size: 20px;
      font-weight: 850;
      height: 58px;
      justify-content: center;
      width: 58px;
    }

    h1 {
      font-size: 22px;
      font-weight: 850;
      line-height: 1.1;
      margin: 0 0 4px;
    }

    .profile-hero p:last-child {
      color: var(--ion-color-medium);
      margin: 0;
    }

    .info-list {
      display: grid;
      gap: 10px;
    }

    .info-list ion-card,
    .school-card {
      margin: 0;
    }

    .info-list ion-card-content {
      align-items: center;
      display: grid;
      gap: 14px;
      grid-template-columns: auto 1fr;
    }

    .info-list ion-icon {
      color: var(--ion-color-primary);
      font-size: 24px;
    }

    strong {
      display: block;
      overflow-wrap: anywhere;
    }

    span {
      color: var(--ion-color-medium);
      font-size: 13px;
    }

    ion-chip {
      --background: #eef4ff;
      --color: #1d4ed8;
      border-radius: 8px;
      margin: 4px 6px 4px 0;
    }
  `]
})
export class ProfilePage {
  private alumnoApi = inject(AlumnoApiService);
  profile$ = this.alumnoApi.profile();

  constructor() {
    addIcons({ ribbonOutline, todayOutline, mailOutline, callOutline, schoolOutline, idCardOutline });
  }

  initials(nombre: string, apellido: string): string {
    return `${nombre.charAt(0)}${apellido.charAt(0)}`.toUpperCase();
  }
}
