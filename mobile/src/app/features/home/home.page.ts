import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { inject } from '@angular/core';
import { IonCard, IonCardContent, IonContent, IonHeader, IonTitle, IonToolbar } from '@ionic/angular/standalone';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-home',
  imports: [AsyncPipe, IonCard, IonCardContent, IonContent, IonHeader, IonTitle, IonToolbar],
  template: `
    <ion-header><ion-toolbar><ion-title>Inicio</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      @if (me$ | async; as me) {
        <h1>Hola, {{ me.nombre_completo }}</h1>
        <ion-card><ion-card-content><strong>Cinturón actual</strong><p>{{ me.cinturon_actual?.nombre || '-' }}</p></ion-card-content></ion-card>
        <ion-card><ion-card-content><strong>Escuelas activas</strong><p>{{ me.escuelas_activas.length }}</p></ion-card-content></ion-card>
      }
    </ion-content>
  `
})
export class HomePage {
  private alumnoApi = inject(AlumnoApiService);
  me$ = this.alumnoApi.me();
}
