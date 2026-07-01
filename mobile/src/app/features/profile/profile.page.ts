import { AsyncPipe, DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { inject } from '@angular/core';
import { IonCard, IonCardContent, IonContent, IonHeader, IonTitle, IonToolbar } from '@ionic/angular/standalone';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-profile',
  imports: [AsyncPipe, DatePipe, IonCard, IonCardContent, IonContent, IonHeader, IonTitle, IonToolbar],
  template: `
    <ion-header><ion-toolbar><ion-title>Perfil</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      @if (profile$ | async; as profile) {
        <ion-card><ion-card-content><strong>{{ profile.apellido }}, {{ profile.nombre }}</strong><p>DNI {{ profile.dni }}</p></ion-card-content></ion-card>
        <ion-card><ion-card-content><strong>Nacimiento</strong><p>{{ profile.fecha_nacimiento | date:'dd/MM/yyyy' }}</p></ion-card-content></ion-card>
        <ion-card><ion-card-content><strong>Contacto</strong><p>{{ profile.email || '-' }} · {{ profile.telefono || '-' }}</p></ion-card-content></ion-card>
      }
    </ion-content>
  `
})
export class ProfilePage {
  private alumnoApi = inject(AlumnoApiService);
  profile$ = this.alumnoApi.profile();
}
