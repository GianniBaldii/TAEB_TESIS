import { Component } from '@angular/core';
import { IonIcon, IonLabel, IonRouterOutlet, IonTabBar, IonTabButton, IonTabs } from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { barChartOutline, clipboardOutline, homeOutline, personOutline } from 'ionicons/icons';

@Component({
  standalone: true,
  selector: 'app-tabs',
  imports: [IonIcon, IonLabel, IonRouterOutlet, IonTabBar, IonTabButton, IonTabs],
  template: `
    <ion-tabs>
      <ion-router-outlet></ion-router-outlet>
      <ion-tab-bar slot="bottom">
        <ion-tab-button tab="home" href="/tabs/home"><ion-icon name="home-outline"></ion-icon><ion-label>Inicio</ion-label></ion-tab-button>
        <ion-tab-button tab="profile" href="/tabs/profile"><ion-icon name="person-outline"></ion-icon><ion-label>Perfil</ion-label></ion-tab-button>
        <ion-tab-button tab="progress" href="/tabs/progress"><ion-icon name="bar-chart-outline"></ion-icon><ion-label>Progreso</ion-label></ion-tab-button>
        <ion-tab-button tab="exams" href="/tabs/exams"><ion-icon name="clipboard-outline"></ion-icon><ion-label>Exámenes</ion-label></ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  `
})
export class TabsPage {
  constructor() {
    addIcons({ homeOutline, personOutline, barChartOutline, clipboardOutline });
  }
}
