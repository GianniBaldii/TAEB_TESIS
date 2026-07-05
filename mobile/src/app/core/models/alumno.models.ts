export interface Cinturon {
  id: number;
  nombre: string;
  tipo_rango: string;
  numeracion: number;
}

export interface EscuelaActiva {
  id: number;
  nombre: string;
}

export interface AlumnoMe {
  nombre_completo: string;
  escuelas_activas: EscuelaActiva[];
  cinturon_actual: Cinturon | null;
}

export interface AlumnoProfile {
  nombre: string;
  apellido: string;
  dni: string;
  fecha_nacimiento: string | null;
  email: string | null;
  telefono: string | null;
  escuelas_activas: EscuelaActiva[];
  cinturon_actual: Cinturon | null;
}

export interface AlumnoExam {
  id: number;
  fecha_examen: string;
  lugar: string;
  estado: string;
  nota_final: string | null;
  cinturon_origen: Cinturon | null;
  cinturon_destino: Cinturon | null;
  es_historico: boolean;
}
