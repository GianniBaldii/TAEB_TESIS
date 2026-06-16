from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AlumnoForm,
    CrearExamenForm,
    ExamenTemplateForm,
    ExamenTemplateItemForm,
    ExamenTemplateSeccionForm,
)
from .models import (
    Alumno,
    Cinturon,
    Examen,
    ExamenDetalle,
    ExamenTemplate,
    ExamenTemplateItem,
    ExamenTemplateSeccion,
)
from .services import alumno_service, examen_alumno_service, examen_template_service
from .services.excepciones import AlumnosError


def _alumno_queryset():
    return Alumno.objects.select_related("cinturon_actual")


def _examen_queryset(alumno):
    return Examen.objects.filter(alumno=alumno).select_related(
        "alumno", "examen_template", "cinturon_origen", "cinturon_destino"
    )


@login_required
def alumno_list(request):
    alumnos = _alumno_queryset()
    busqueda = request.GET.get("q", "").strip()
    activo = request.GET.get("activo", "")
    cinturon_id = request.GET.get("cinturon", "")

    if busqueda:
        alumnos = alumnos.filter(
            Q(nombre__icontains=busqueda)
            | Q(apellido__icontains=busqueda)
            | Q(dni__icontains=busqueda)
        )
    if activo in {"1", "0"}:
        alumnos = alumnos.filter(activo=activo == "1")
    if cinturon_id:
        alumnos = alumnos.filter(cinturon_actual_id=cinturon_id)

    return render(
        request,
        "alumnos/alumno_list.html",
        {
            "alumnos": alumnos,
            "cinturones": Cinturon.objects.filter(activo=True),
            "filtros": {"q": busqueda, "activo": activo, "cinturon": cinturon_id},
            "titulo_pagina": "Alumnos",
        },
    )


@login_required
def alumno_create(request):
    form = AlumnoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        alumno = alumno_service.crear_alumno(form.cleaned_data)
        messages.success(request, "Alumno creado correctamente.")
        return redirect("alumnos:alumno_detail", pk=alumno.pk)
    return render(request, "alumnos/alumno_form.html", {"form": form, "modo": "crear"})


@login_required
def alumno_update(request, pk):
    alumno = get_object_or_404(_alumno_queryset(), pk=pk)
    form = AlumnoForm(request.POST or None, instance=alumno)
    if request.method == "POST" and form.is_valid():
        alumno_service.actualizar_alumno(alumno, form.cleaned_data)
        messages.success(request, "Alumno actualizado correctamente.")
        return redirect("alumnos:alumno_detail", pk=alumno.pk)
    return render(
        request,
        "alumnos/alumno_form.html",
        {"form": form, "alumno": alumno, "modo": "editar"},
    )


@login_required
def alumno_detail(request, pk):
    alumno = get_object_or_404(_alumno_queryset(), pk=pk)
    examenes = _examen_queryset(alumno).exclude(estado=Examen.Estado.ANULADO)
    historial = alumno.historial_cinturones.select_related("cinturon", "examen")
    return render(
        request,
        "alumnos/alumno_detail.html",
        {
            "alumno": alumno,
            "progreso": alumno_service.obtener_progreso_alumno(alumno),
            "examenes": examenes,
            "historial": historial,
        },
    )


@login_required
def alumno_baja(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        alumno_service.dar_baja_alumno(alumno)
        messages.success(request, "Alumno dado de baja correctamente.")
    return redirect("alumnos:alumno_list")


@login_required
def alumno_reactivar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        alumno_service.reactivar_alumno(alumno)
        messages.success(request, "Alumno reactivado correctamente.")
    return redirect("alumnos:alumno_list")


@login_required
def examen_create(request, alumno_id):
    alumno = get_object_or_404(_alumno_queryset(), pk=alumno_id)
    form = CrearExamenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            examen = examen_alumno_service.crear_examen_para_alumno(
                alumno=alumno,
                fecha_examen=form.cleaned_data["fecha_examen"],
                lugar=form.cleaned_data["lugar"],
                cinturon_origen=form.cleaned_data["cinturon_origen"],
                cinturon_destino=form.cleaned_data["cinturon_destino"],
                es_historico=form.cleaned_data["es_historico"],
            )
        except AlumnosError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Examen creado correctamente.")
            return redirect(
                "alumnos:examen_evaluaciones", alumno_id=alumno.pk, examen_id=examen.pk
            )
    return render(
        request,
        "alumnos/examenes/examen_form.html",
        {"form": form, "alumno": alumno},
    )


def _obtener_examen(alumno_id, examen_id):
    alumno = get_object_or_404(_alumno_queryset(), pk=alumno_id)
    examen = get_object_or_404(_examen_queryset(alumno), pk=examen_id)
    return alumno, examen


@login_required
def examen_detail(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(alumno_id, examen_id)
    detalles = examen.detalles.select_related("template_item", "template_item__seccion")
    return render(
        request,
        "alumnos/examenes/examen_detail.html",
        {"alumno": alumno, "examen": examen, "detalles": detalles},
    )


@login_required
def examen_evaluaciones(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(alumno_id, examen_id)
    if examen_alumno_service.examen_tiene_estado_final(examen):
        messages.error(
            request,
            "No se pueden editar evaluaciones de un examen con estado final.",
        )
        return redirect("alumnos:examen_detail", alumno_id=alumno.pk, examen_id=examen.pk)
    detalles = examen.detalles.select_related("template_item", "template_item__seccion")
    if request.method == "POST":
        data = {"detalles": {}}
        for detalle in detalles:
            base = f"detalle_{detalle.pk}_"
            aprobado = request.POST.get(base + "aprobado")
            data["detalles"][detalle.pk] = {
                "nota_numerica": request.POST.get(base + "nota_numerica"),
                "concepto": request.POST.get(base + "concepto"),
                "valor_texto": request.POST.get(base + "valor_texto"),
                "aprobado": aprobado,
                "observaciones": request.POST.get(base + "observaciones"),
            }
        data["nota_final"] = request.POST.get("nota_final")
        data["resultado_final"] = request.POST.get("resultado_final")
        data["observaciones"] = request.POST.get("observaciones")
        try:
            examen_alumno_service.actualizar_evaluaciones_examen(examen, data)
        except AlumnosError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Evaluaciones guardadas correctamente.")
        return redirect("alumnos:examen_detail", alumno_id=alumno.pk, examen_id=examen.pk)
    return render(
        request,
        "alumnos/examenes/examen_evaluaciones_form.html",
        {"alumno": alumno, "examen": examen, "detalles": detalles},
    )


@login_required
def examen_aprobar(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(alumno_id, examen_id)
    if request.method == "POST":
        try:
            examen_alumno_service.aprobar_examen(examen)
        except AlumnosError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Examen aprobado correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)


@login_required
def examen_desaprobar(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(alumno_id, examen_id)
    if request.method == "POST":
        try:
            examen_alumno_service.desaprobar_examen(examen)
        except AlumnosError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Examen desaprobado correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)


@login_required
def examen_anular(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(alumno_id, examen_id)
    if request.method == "POST":
        try:
            examen_alumno_service.anular_examen(examen)
        except AlumnosError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Examen anulado correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)


@login_required
def template_list(request):
    templates = ExamenTemplate.objects.select_related("cinturon")
    cinturon_id = request.GET.get("cinturon", "")
    activo = request.GET.get("activo", "")
    tipo_rango = request.GET.get("tipo_rango", "")
    if cinturon_id:
        templates = templates.filter(cinturon_id=cinturon_id)
    if activo in {"1", "0"}:
        templates = templates.filter(activo=activo == "1")
    if tipo_rango:
        templates = templates.filter(cinturon__tipo_rango=tipo_rango)
    return render(
        request,
        "alumnos/templates_examen/examen_template_list.html",
        {
            "templates": templates,
            "cinturones": Cinturon.objects.filter(activo=True),
            "filtros": {
                "cinturon": cinturon_id,
                "activo": activo,
                "tipo_rango": tipo_rango,
            },
        },
    )


@login_required
def template_create(request):
    form = ExamenTemplateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        template = examen_template_service.crear_template(form.cleaned_data)
        messages.success(request, "Template creado correctamente.")
        return redirect("alumnos:template_detail", pk=template.pk)
    return render(
        request,
        "alumnos/templates_examen/examen_template_form.html",
        {"form": form, "modo": "crear"},
    )


@login_required
def template_update(request, pk):
    template = get_object_or_404(ExamenTemplate.objects.select_related("cinturon"), pk=pk)
    form = ExamenTemplateForm(request.POST or None, instance=template)
    if request.method == "POST" and form.is_valid():
        examen_template_service.actualizar_template(template, form.cleaned_data)
        messages.success(request, "Template actualizado correctamente.")
        return redirect("alumnos:template_detail", pk=template.pk)
    return render(
        request,
        "alumnos/templates_examen/examen_template_form.html",
        {"form": form, "template_examen": template, "modo": "editar"},
    )


@login_required
def template_detail(request, pk):
    template = get_object_or_404(
        ExamenTemplate.objects.select_related("cinturon").prefetch_related(
            Prefetch(
                "secciones",
                queryset=ExamenTemplateSeccion.objects.order_by("orden").prefetch_related(
                    Prefetch(
                        "items",
                        queryset=ExamenTemplateItem.objects.order_by("orden"),
                    )
                ),
            )
        ),
        pk=pk,
    )
    return render(
        request,
        "alumnos/templates_examen/examen_template_detail.html",
        {"template_examen": template},
    )


@login_required
def template_activar(request, pk):
    template = get_object_or_404(ExamenTemplate, pk=pk)
    if request.method == "POST":
        examen_template_service.activar_template(template)
        messages.success(request, "Template activado correctamente.")
    return redirect("alumnos:template_detail", pk=template.pk)


@login_required
def template_desactivar(request, pk):
    template = get_object_or_404(ExamenTemplate, pk=pk)
    if request.method == "POST":
        examen_template_service.desactivar_template(template)
        messages.success(request, "Template desactivado correctamente.")
    return redirect("alumnos:template_detail", pk=template.pk)


@login_required
def seccion_create(request, template_id):
    template = get_object_or_404(ExamenTemplate, pk=template_id)
    form = ExamenTemplateSeccionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        examen_template_service.crear_seccion(template, form.cleaned_data)
        messages.success(request, "Seccion creada correctamente.")
        return redirect("alumnos:template_detail", pk=template.pk)
    return render(
        request,
        "alumnos/templates_examen/seccion_form.html",
        {"form": form, "template_examen": template},
    )


@login_required
def seccion_update(request, seccion_id):
    seccion = get_object_or_404(ExamenTemplateSeccion.objects.select_related("examen_template"), pk=seccion_id)
    form = ExamenTemplateSeccionForm(request.POST or None, instance=seccion)
    if request.method == "POST" and form.is_valid():
        examen_template_service.actualizar_seccion(seccion, form.cleaned_data)
        messages.success(request, "Seccion actualizada correctamente.")
        return redirect("alumnos:template_detail", pk=seccion.examen_template_id)
    return render(
        request,
        "alumnos/templates_examen/seccion_form.html",
        {"form": form, "seccion": seccion, "template_examen": seccion.examen_template},
    )


@login_required
def seccion_desactivar(request, seccion_id):
    seccion = get_object_or_404(ExamenTemplateSeccion, pk=seccion_id)
    if request.method == "POST":
        examen_template_service.desactivar_seccion(seccion)
        messages.success(request, "Seccion desactivada correctamente.")
    return redirect("alumnos:template_detail", pk=seccion.examen_template_id)


@login_required
def item_create(request, seccion_id):
    seccion = get_object_or_404(ExamenTemplateSeccion.objects.select_related("examen_template"), pk=seccion_id)
    form = ExamenTemplateItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        examen_template_service.crear_item(seccion, form.cleaned_data)
        messages.success(request, "Item creado correctamente.")
        return redirect("alumnos:template_detail", pk=seccion.examen_template_id)
    return render(
        request,
        "alumnos/templates_examen/item_form.html",
        {"form": form, "seccion": seccion, "template_examen": seccion.examen_template},
    )


@login_required
def item_update(request, item_id):
    item = get_object_or_404(
        ExamenTemplateItem.objects.select_related("seccion", "seccion__examen_template"),
        pk=item_id,
    )
    form = ExamenTemplateItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        examen_template_service.actualizar_item(item, form.cleaned_data)
        messages.success(request, "Item actualizado correctamente.")
        return redirect("alumnos:template_detail", pk=item.seccion.examen_template_id)
    return render(
        request,
        "alumnos/templates_examen/item_form.html",
        {"form": form, "item": item, "seccion": item.seccion, "template_examen": item.seccion.examen_template},
    )


@login_required
def item_desactivar(request, item_id):
    item = get_object_or_404(ExamenTemplateItem.objects.select_related("seccion"), pk=item_id)
    if request.method == "POST":
        examen_template_service.desactivar_item(item)
        messages.success(request, "Item desactivado correctamente.")
    return redirect("alumnos:template_detail", pk=item.seccion.examen_template_id)
