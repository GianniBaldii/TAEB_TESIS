import { Cinturon } from './alumno.models';

export interface AlumnoProgress {
  cinturon_actual: Cinturon | null;
  proximo_cinturon: Cinturon | null;
  tiempo_desde_ultimo_cinturon: string;
  tiempo_orientativo: string;
  estado_orientativo: {
    codigo: string;
    label: string;
    mensaje: string;
    porcentaje: number;
  };
  promociones_obtenidas: number;
  examenes_aprobados: number;
  examenes_desaprobados: number;
}
