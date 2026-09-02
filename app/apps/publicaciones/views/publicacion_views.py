from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from apps.escuelas.models import Escuela
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario

from ..forms import PublicacionForm
from ..models import Publicacion
from ..selectors import publicaciones_visibles_para_usuario
from ..services import publicacion_service
from ..services.excepciones import PublicacionesError


def _publicacion_accesible(request, publicacion_id):
    return get_object_or_404(
        publicaciones_visibles_para_usuario(request.user),
        pk=publicacion_id,
    )


def _ejecutar_accion(request, publicacion_id, accion, mensaje):
    publicacion = _publicacion_accesible(request, publicacion_id)
    if request.method == "POST":
        try:
            accion(publicacion, usuario=request.user)
        except PublicacionesError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, mensaje)
    return redirect("publicaciones:publicacion_detail", publicacion_id=publicacion.pk)


@login_required
def publicacion_list(request):
    publicaciones = publicaciones_visibles_para_usuario(request.user)
    filtros = {
        "q": request.GET.get("q", "").strip(),
        "escuela": request.GET.get("escuela", ""),
        "tipo": request.GET.get("tipo", ""),
        "tematica": request.GET.get("tematica", ""),
        "estado": request.GET.get("estado", ""),
        "activo": request.GET.get("activo", "1"),
        "fecha": request.GET.get("fecha", ""),
    }
    # Buscador: acepta cualquier texto
    if filtros["q"]:
        publicaciones = publicaciones.filter(
            Q(titulo__icontains=filtros["q"])
            | Q(descripcion__icontains=filtros["q"])
        )


    # Escuela: solo se usa para administradores
    if request.user.is_superuser and filtros["escuela"]:
        if filtros["escuela"].isdigit():
            publicaciones = publicaciones.filter(
                escuela_id=filtros["escuela"]
            )
        else:
            messages.warning(
                request,
                "La escuela indicada no es válida."
            )
            publicaciones = publicaciones.none()


    # Tipo: solamente ANUNCIO o EVENTO
    if filtros["tipo"]:
        if filtros["tipo"] in Publicacion.Tipo.values:
            publicaciones = publicaciones.filter(
                tipo_publicacion=filtros["tipo"]
            )
        else:
            messages.warning(
                request,
                "El tipo de publicación indicado no es válido."
            )
            publicaciones = publicaciones.none()


    # Temática: solamente las temáticas registradas
    if filtros["tematica"]:
        if filtros["tematica"] in Publicacion.Tematica.values:
            publicaciones = publicaciones.filter(
                tematica=filtros["tematica"]
            )
        else:
            messages.warning(
                request,
                "La temática indicada no es válida."
            )
            publicaciones = publicaciones.none()


    # Estado: solamente los estados registrados
    if filtros["estado"]:
        if filtros["estado"] in Publicacion.Estado.values:
            publicaciones = publicaciones.filter(
                estado=filtros["estado"]
            )
        else:
            messages.warning(
                request,
                "El estado indicado no es válido."
            )
            publicaciones = publicaciones.none()


    # Activo: solamente 1, 0 o vacío
    if filtros["activo"] in {"1", "0"}:
        publicaciones = publicaciones.filter(
            activo=filtros["activo"] == "1"
        )
    elif filtros["activo"] != "":
        messages.warning(
            request,
            "El estado de actividad indicado no es válido."
        )
        publicaciones = publicaciones.none()


    # Fecha
    if filtros["fecha"]:
        fecha = parse_date(filtros["fecha"])

        if fecha:
            publicaciones = publicaciones.filter(
                fecha_hora_inicio__date=fecha
            )
        else:
            messages.warning(
                request,
                "La fecha indicada no tiene un formato válido."
            )
            publicaciones = publicaciones.none()
    return render(
        request,
        "publicaciones/publicacion_list.html",
        {
            "publicaciones": publicaciones,
            "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else [],
            "tipos": Publicacion.Tipo.choices,
            "tematicas": Publicacion.Tematica.choices,
            "estados": Publicacion.Estado.choices,
            "filtros": filtros,
        },
    )


@login_required
def publicacion_create(request):
    permitir_escuela = request.user.is_superuser
    escuela = None if permitir_escuela else obtener_escuela_activa_usuario(request.user)
    form = PublicacionForm(request.POST or None, permitir_escuela=permitir_escuela)
    if request.method == "POST" and form.is_valid():
        if permitir_escuela:
            escuela = form.cleaned_data["escuela"]
        try:
            publicacion = publicacion_service.crear_publicacion(
                escuela=escuela,
                usuario=request.user,
                data=form.cleaned_data,
            )
        except PublicacionesError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, "Publicación creada como borrador.")
            return redirect("publicaciones:publicacion_detail", publicacion_id=publicacion.pk)
    return render(request, "publicaciones/publicacion_form.html", {"form": form, "modo": "crear"})


@login_required
def publicacion_update(request, publicacion_id):
    publicacion = _publicacion_accesible(request, publicacion_id)
    if not publicacion.activo or publicacion.estado != Publicacion.Estado.BORRADOR:
        messages.error(request, "Solo se pueden editar publicaciones activas en borrador.")
        return redirect("publicaciones:publicacion_detail", publicacion_id=publicacion.pk)
    form = PublicacionForm(request.POST or None, instance=publicacion, permitir_escuela=False)
    if request.method == "POST" and form.is_valid():
        try:
            publicacion_service.actualizar_publicacion(
                publicacion,
                usuario=request.user,
                data=form.cleaned_data,
            )
        except PublicacionesError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, "Publicación actualizada correctamente.")
            return redirect("publicaciones:publicacion_detail", publicacion_id=publicacion.pk)
    return render(
        request,
        "publicaciones/publicacion_form.html",
        {"form": form, "modo": "editar", "publicacion": publicacion},
    )


@login_required
def publicacion_detail(request, publicacion_id):
    return render(
        request,
        "publicaciones/publicacion_detail.html",
        {"publicacion": _publicacion_accesible(request, publicacion_id)},
    )


@login_required
@require_POST
def publicacion_publicar(request, publicacion_id):
    return _ejecutar_accion(
        request,
        publicacion_id,
        publicacion_service.publicar_publicacion,
        "Publicación publicada correctamente.",
    )


@login_required
@require_POST
def publicacion_cancelar(request, publicacion_id):
    return _ejecutar_accion(
        request,
        publicacion_id,
        publicacion_service.cancelar_publicacion,
        "Evento cancelado correctamente.",
    )


@login_required
@require_POST
def publicacion_finalizar(request, publicacion_id):
    return _ejecutar_accion(
        request,
        publicacion_id,
        publicacion_service.finalizar_publicacion,
        "Evento finalizado correctamente.",
    )


@login_required
@require_POST
def publicacion_desactivar(request, publicacion_id):
    return _ejecutar_accion(
        request,
        publicacion_id,
        publicacion_service.desactivar_publicacion,
        "Publicación desactivada correctamente.",
    )
