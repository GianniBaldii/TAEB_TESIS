from .alumno_views import alumno_baja, alumno_create, alumno_detail, alumno_list, alumno_reactivar, alumno_update
from .credencial_views import alumno_credencial_bloquear, alumno_credencial_generar, alumno_credencial_reactivar, alumno_credencial_resetear_password, alumno_credencial_revocar_sesiones
from .examen_views import examen_anular, examen_aprobar, examen_create, examen_desaprobar, examen_detail, examen_evaluaciones
from .examen_template_views import item_create, item_desactivar, item_update, seccion_create, seccion_desactivar, seccion_update, template_activar, template_create, template_desactivar, template_detail, template_duplicar, template_eliminar, template_list, template_update

__all__ = [name for name in globals() if not name.startswith("_")]
