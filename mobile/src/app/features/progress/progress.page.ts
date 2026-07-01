import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { inject } from '@angular/core';
import { IonCard, IonCardContent, IonContent, IonHeader, IonProgressBar, IonTitle, IonToolbar } from '@ionic/angular/standalone';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-progress',
  imports: [AsyncPipe, IonCard, IonCardContent, IonContent, IonHeader, IonProgressBar, IonTitle, IonToolbar],
  template: `
    <ion-header><ion-toolbar><ion-title>Progreso</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      @if (progress$ | async; as progress) {
        <ion-card><ion-card-content><strong>Objetivo</strong><p>{{ progress.proximo_cinturon?.nombre || '-' }}</p><ion-progress-bar [value]="progress.estado_orientativo.porcentaje / 100"></ion-progress-bar></ion-card-content></ion-card>
        <ion-card><ion-card-content><strong>{{ progress.estado_orientativo.label }}</strong><p>{{ progress.estado_orientativo.mensaje }}</p></ion-card-content></ion-card>
      }
    </ion-content>
  `
})
export class ProgressPage {
  private alumnoApi = inject(AlumnoApiService);
  progress$ = this.alumnoApi.progress();
}
