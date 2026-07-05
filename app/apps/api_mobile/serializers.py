from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.alumnos.models import AlumnoCredencial, AlumnoEscuela, Examen
from apps.alumnos.services.excepciones import AlumnosError
from apps.alumnos.services import alumno_credencial_service, trayectoria_taekwondista_service


MENSAJE_LOGIN_INVALIDO = "DNI o contrasena incorrectos."


def _cinturon_data(cinturon):
    if not cinturon:
        return None
    return {
        "id": cinturon.id,
        "nombre": cinturon.nombre,
        "tipo_rango": cinturon.tipo_rango,
        "numeracion": cinturon.numeracion,
    }


def _escuelas_activas(alumno):
    return [
        {"id": inscripcion.escuela_id, "nombre": str(inscripcion.escuela)}
        for inscripcion in AlumnoEscuela.objects.select_related("escuela").filter(
            alumno=alumno,
            activo=True,
            escuela__activo=True,
        )
    ]


class MobileLoginSerializer(serializers.Serializer):
    dni = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            username = alumno_credencial_service.normalizar_dni_para_username(attrs["dni"])
        except AlumnosError as exc:
            raise serializers.ValidationError(MENSAJE_LOGIN_INVALIDO) from exc
        usuario = get_user_model().objects.filter(username=username).first()
        credencial = None
        if usuario:
            credencial = getattr(usuario, "credencial_alumno", None)
        if credencial and alumno_credencial_service.credencial_tiene_bloqueo_temporal_activo(
            credencial
        ):
            raise serializers.ValidationError(MENSAJE_LOGIN_INVALIDO)

        usuario_autenticado = authenticate(
            username=username,
            password=attrs["password"],
        )
        if not usuario_autenticado or not credencial:
            if credencial:
                alumno_credencial_service.registrar_login_fallido(credencial)
            raise serializers.ValidationError(MENSAJE_LOGIN_INVALIDO)
        if (
            not usuario_autenticado.is_active
            or not credencial.acceso_habilitado
            or not credencial.alumno.activo
            or not AlumnoEscuela.objects.filter(
                alumno=credencial.alumno,
                activo=True,
                escuela__activo=True,
            ).exists()
        ):
            alumno_credencial_service.registrar_login_fallido(credencial)
            raise serializers.ValidationError(MENSAJE_LOGIN_INVALIDO)

        alumno_credencial_service.registrar_login_exitoso(credencial)
        refresh = RefreshToken.for_user(usuario_autenticado)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "debe_cambiar_password": credencial.debe_cambiar_password,
        }


class AlumnoMeSerializer(serializers.Serializer):
    def to_representation(self, alumno):
        return {
            "nombre_completo": f"{alumno.nombre} {alumno.apellido}".strip(),
            "escuelas_activas": _escuelas_activas(alumno),
            "cinturon_actual": _cinturon_data(alumno.cinturon_actual),
        }


class AlumnoProfileSerializer(serializers.Serializer):
    def to_representation(self, alumno):
        return {
            "nombre": alumno.nombre,
            "apellido": alumno.apellido,
            "dni": alumno.dni,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "email": alumno.email,
            "telefono": alumno.telefono,
            "escuelas_activas": _escuelas_activas(alumno),
            "cinturon_actual": _cinturon_data(alumno.cinturon_actual),
        }


class AlumnoProgressSerializer(serializers.Serializer):
    def to_representation(self, alumno):
        analisis = trayectoria_taekwondista_service.obtener_analisis_trayectoria(alumno)
        estado = analisis["estado_habilitacion"]
        return {
            "cinturon_actual": _cinturon_data(analisis["cinturon_actual"]),
            "proximo_cinturon": _cinturon_data(analisis["proximo_cinturon"]),
            "tiempo_desde_ultimo_cinturon": analisis["tiempo_desde_ultimo_cinturon"],
            "tiempo_orientativo": analisis["tiempo_orientativo_label"],
            "estado_orientativo": {
                "codigo": estado["codigo"],
                "label": estado["label"],
                "mensaje": estado["mensaje"],
                "porcentaje": estado["porcentaje"],
            },
            "promociones_obtenidas": analisis["promociones_obtenidas"],
            "examenes_aprobados": analisis["cantidad_aprobados"],
            "examenes_desaprobados": analisis["cantidad_desaprobados"],
        }


class AlumnoBeltHistorySerializer(serializers.Serializer):
    def to_representation(self, hito):
        return {
            "id": hito.id,
            "cinturon": _cinturon_data(hito.cinturon),
            "fecha_obtencion": hito.fecha_obtencion,
            "observaciones": hito.observaciones,
        }


class AlumnoExamSerializer(serializers.Serializer):
    def to_representation(self, examen):
        return {
            "id": examen.id,
            "fecha_examen": examen.fecha_examen,
            "lugar": examen.lugar,
            "estado": examen.estado,
            "nota_final": examen.nota_final,
            "cinturon_origen": _cinturon_data(examen.cinturon_origen),
            "cinturon_destino": _cinturon_data(examen.cinturon_destino),
            "es_historico": examen.es_historico,
        }
