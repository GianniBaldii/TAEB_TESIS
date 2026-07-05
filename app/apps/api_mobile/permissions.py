from rest_framework.permissions import BasePermission

from apps.alumnos.models import AlumnoEscuela


class EsAlumnoMobileAutenticado(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated or not usuario.is_active:
            return False
        credencial = getattr(usuario, "credencial_alumno", None)
        if not credencial or not credencial.acceso_habilitado:
            return False
        alumno = credencial.alumno
        if not alumno.activo:
            return False
        return AlumnoEscuela.objects.filter(
            alumno=alumno,
            activo=True,
            escuela__activo=True,
        ).exists()

