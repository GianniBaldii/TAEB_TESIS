from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from apps.alumnos.models import Examen

from .permissions import EsAlumnoMobileAutenticado
from .serializers import (
    AlumnoBeltHistorySerializer,
    AlumnoExamSerializer,
    AlumnoMeSerializer,
    AlumnoProfileSerializer,
    AlumnoProgressSerializer,
    MobileLoginSerializer,
)


class MobileLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MobileLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class MobileRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class MobileLogoutView(APIView):
    permission_classes = [EsAlumnoMobileAutenticado]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Refresh token invalido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlumnoMobileBaseView(APIView):
    permission_classes = [EsAlumnoMobileAutenticado]

    def obtener_alumno(self):
        return self.request.user.credencial_alumno.alumno


class MobileMeView(AlumnoMobileBaseView):
    def get(self, request):
        return Response(AlumnoMeSerializer(self.obtener_alumno()).data)


class MobileProfileView(AlumnoMobileBaseView):
    def get(self, request):
        return Response(AlumnoProfileSerializer(self.obtener_alumno()).data)


class MobileProgressView(AlumnoMobileBaseView):
    def get(self, request):
        return Response(AlumnoProgressSerializer(self.obtener_alumno()).data)


class MobileBeltHistoryView(AlumnoMobileBaseView):
    def get(self, request):
        historial = self.obtener_alumno().historial_cinturones.select_related(
            "cinturon"
        ).order_by("fecha_obtencion", "cinturon__orden")
        return Response(AlumnoBeltHistorySerializer(historial, many=True).data)


class MobileExamsView(AlumnoMobileBaseView):
    def get(self, request):
        examenes = (
            Examen.objects.select_related("cinturon_origen", "cinturon_destino")
            .filter(alumno=self.obtener_alumno())
            .exclude(estado=Examen.Estado.ANULADO)
            .order_by("-fecha_examen", "-fecha_creacion")
        )
        return Response(AlumnoExamSerializer(examenes, many=True).data)
