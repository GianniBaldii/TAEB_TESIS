import { Component } from '@angular/core';
import { inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonButton,
  IonCard,
  IonCardContent,
  IonContent,
  IonInput,
  IonItem,
  IonLabel,
  IonText
} from '@ionic/angular/standalone';

import { AuthService } from '../../../core/auth/auth.service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [
    ReactiveFormsModule,
    IonButton,
    IonCard,
    IonCardContent,
    IonContent,
    IonInput,
    IonItem,
    IonLabel,
    IonText
  ],
  template: `
    <ion-content class="ion-padding">
      <div class="login-shell">
        <ion-card>
          <ion-card-content>
            <h1>TAEB</h1>
            <p class="helper">Las credenciales de acceso deben ser solicitadas a su escuela.</p>
            <form [formGroup]="form" (ngSubmit)="submit()">
              <ion-item>
                <ion-label position="stacked">DNI</ion-label>
                <ion-input formControlName="dni" inputmode="numeric" autocomplete="username"></ion-input>
              </ion-item>
              <ion-item>
                <ion-label position="stacked">Contraseña</ion-label>
                <ion-input formControlName="password" type="password" autocomplete="current-password"></ion-input>
              </ion-item>
              @if (error) {
                <ion-text color="danger"><p>{{ error }}</p></ion-text>
              }
              <ion-button expand="block" type="submit" [disabled]="form.invalid || loading">
                {{ loading ? 'Ingresando...' : 'Ingresar' }}
              </ion-button>
            </form>
          </ion-card-content>
        </ion-card>
      </div>
    </ion-content>
  `,
  styles: [`
    .login-shell { min-height: 100%; display: grid; place-items: center; }
    ion-card { width: 100%; max-width: 420px; }
    h1 { margin: 0 0 8px; font-size: 32px; font-weight: 800; }
    .helper { color: var(--ion-color-medium); margin-bottom: 20px; }
    ion-button { margin-top: 20px; }
  `]
})
export class LoginPage {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  loading = false;
  error = '';
  form = this.fb.nonNullable.group({
    dni: ['', Validators.required],
    password: ['', Validators.required]
  });

  async submit(): Promise<void> {
    this.loading = true;
    this.error = '';
    try {
      await this.auth.login(this.form.getRawValue());
      await this.router.navigateByUrl('/tabs/home', { replaceUrl: true });
    } catch {
      this.error = 'DNI o contraseña incorrectos.';
    } finally {
      this.loading = false;
    }
  }
}
