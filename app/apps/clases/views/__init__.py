from .asistencia_views import asistencia_form, cancelar_sesion, cerrar_asistencia, marcar_todos_presentes, reabrir_asistencia, sesion_detail
from .calendario_views import abrir_ocurrencia, calendario, clase_extra_create
from .clase_views import clase_create, clase_detail, clase_estado, clase_list, clase_update
from .horario_views import horario_create, horario_desactivar, horario_update
from .inscripcion_views import clase_alumno_baja, clase_alumno_create, clase_alumno_reactivar
__all__=[name for name in globals() if not name.startswith("_")]
