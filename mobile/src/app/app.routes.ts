import { Routes } from '@angular/router';

import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: 'auth/login',
    loadComponent: () =>
      import('./features/auth/login/login.page').then((m) => m.LoginPage)
  },
  {
    path: 'tabs',
    canActivate: [authGuard],
    loadComponent: () => import('./features/tabs/tabs.page').then((m) => m.TabsPage),
    children: [
      { path: 'home', loadComponent: () => import('./features/home/home.page').then((m) => m.HomePage) },
      { path: 'profile', loadComponent: () => import('./features/profile/profile.page').then((m) => m.ProfilePage) },
      { path: 'progress', loadComponent: () => import('./features/progress/progress.page').then((m) => m.ProgressPage) },
      { path: 'exams', loadComponent: () => import('./features/exams/exams.page').then((m) => m.ExamsPage) },
      { path: '', redirectTo: 'home', pathMatch: 'full' }
    ]
  },
  { path: '', redirectTo: 'auth/login', pathMatch: 'full' }
];
