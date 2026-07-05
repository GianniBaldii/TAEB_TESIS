import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import {
  IonButton,
  IonCard,
  IonCardContent,
  IonContent,
  IonIcon,
  IonInput,
  IonItem,
  IonLabel,
  IonSpinner,
  IonText
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { idCardOutline, lockClosedOutline } from 'ionicons/icons';

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
    IonIcon,
    IonInput,
    IonItem,
    IonLabel,
    IonSpinner,
    IonText
  ],
  template: `
    <ion-content class="ion-padding login-content">
      <main class="login-shell">
        <section class="brand-panel">
          <img class="brand-logo" src="assets/taeb-logo.svg" alt="TAEB">
          <p class="eyebrow">TAEB Mobile</p>
          <h1>Ingreso de alumnos</h1>
          <p class="brand-copy">Consulta tu perfil, progreso y exámenes desde el celular.</p>
        </section>

        <ion-card class="login-card">
          <ion-card-content>
            <form [formGroup]="form" (ngSubmit)="submit()">
              <ion-item lines="none">
                <ion-icon slot="start" name="id-card-outline"></ion-icon>
                <ion-label position="stacked">DNI</ion-label>
                <ion-input formControlName="dni" inputmode="numeric" autocomplete="username"></ion-input>
              </ion-item>

              <ion-item lines="none">
                <ion-icon slot="start" name="lock-closed-outline"></ion-icon>
                <ion-label position="stacked">Contraseña</ion-label>
                <ion-input formControlName="password" type="password" autocomplete="current-password"></ion-input>
              </ion-item>

              @if (error) {
                <ion-text color="danger"><p class="error-text">{{ error }}</p></ion-text>
              }

              <ion-button expand="block" type="submit" [disabled]="form.invalid || loading">
                @if (loading) {
                  <ion-spinner name="crescent"></ion-spinner>
                } @else {
                  Ingresar
                }
              </ion-button>

              <p class="helper">Solicita tus credenciales en tu escuela si todavía no las tienes.</p>
            </form>
          </ion-card-content>
        </ion-card>
      </main>
    </ion-content>
  `,
  styles: [`
    .login-content {
      --background: linear-gradient(180deg, #ffffff 0%, #f4f8ff 48%, #f6f8fc 100%);
    }

    .login-shell {
      align-content: center;
      display: grid;
      gap: 16px;
      margin: 0 auto;
      max-width: 430px;
      min-height: 100%;
      padding: 18px 0;
    }

    .brand-panel {
      background: #ffffff;
      border: 1px solid rgba(23, 32, 51, 0.08);
      border-radius: 8px;
      box-shadow: 0 12px 26px rgba(23, 32, 51, 0.06);
      padding: 20px;
    }

    .brand-logo {
      display: block;
      height: auto;
      margin: 0 0 18px;
      max-width: 210px;
      width: 58%;
    }

    h1 {
      color: #172033;
      font-size: 30px;
      font-weight: 850;
      line-height: 1.08;
      margin: 0 0 8px;
    }

    .brand-copy {
      color: #4b5872;
      font-size: 15px;
      line-height: 1.45;
      margin: 0;
    }

    .login-card {
      margin: 0;
      width: 100%;
    }

    .login-card ion-card-content {
      padding: 18px;
    }

    ion-item {
      --background: #f7f9fd;
      --border-radius: 8px;
      --min-height: 62px;
      border: 1px solid rgba(23, 32, 51, 0.08);
      border-radius: 8px;
      margin-bottom: 12px;
    }

    ion-item ion-icon {
      color: var(--ion-color-primary);
      margin-right: 8px;
    }

    ion-button {
      --border-radius: 8px;
      height: 48px;
      margin-top: 18px;
    }

    ion-spinner {
      height: 20px;
      width: 20px;
    }

    .helper {
      color: var(--ion-color-medium);
      font-size: 13px;
      line-height: 1.4;
      margin: 14px 0 0;
      text-align: center;
    }

    .error-text {
      font-size: 13px;
      margin: 6px 0 0;
    }

    @media (max-width: 380px) {
      .brand-panel {
        padding: 18px;
      }

      .brand-logo {
        max-width: 184px;
        width: 64%;
      }

      h1 {
        font-size: 27px;
      }
    }
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

  constructor() {
    addIcons({ idCardOutline, lockClosedOutline });
  }

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
