export interface AuthTokens {
  access: string;
  refresh: string;
  debe_cambiar_password?: boolean;
}

export interface LoginPayload {
  dni: string;
  password: string;
}
