import { AsyncPipe, DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { inject } from '@angular/core';
import { IonCard, IonCardContent, IonContent, IonHeader, IonTitle, IonToolbar } from '@ionic/angular/standalone';

import { AlumnoApiService } from '../../core/api/alumno-api.service';

@Component({
  standalone: true,
  selector: 'app-exams',
  imports: [AsyncPipe, DatePipe, IonCard, IonCardContent, IonContent, IonHeader, IonTitle, IonToolbar],
  template: `
    <ion-header><ion-toolbar><ion-title>Exámenes</ion-title></ion-toolbar></ion-header>
    <ion-content class="ion-padding">
      @for (exam of exams$ | async; track exam.id) {
        <ion-card><ion-card-content><strong>{{ exam.fecha_examen | date:'dd/MM/yyyy' }} · {{ exam.estado }}</strong><p>{{ exam.cinturon_destino?.nombre || '-' }}</p></ion-card-content></ion-card>
      } @empty {
        <p>No hay exámenes para mostrar.</p>
      }
    </ion-content>
  `
})
export class ExamsPage {
  private alumnoApi = inject(AlumnoApiService);
  exams$ = this.alumnoApi.exams();
}
