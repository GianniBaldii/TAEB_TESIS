from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import ExamenTemplateForm, ExamenTemplateItemForm, ExamenTemplateSeccionForm
from ..models import Cinturon, ExamenTemplate, ExamenTemplateItem, ExamenTemplateSeccion
from ..services import examen_template_service
from ..services.excepciones import AlumnosError
from ._helpers import mensaje_error_validacion

@login_required
def template_list(request):
    templates=ExamenTemplate.objects.select_related("cinturon"); cinturon=request.GET.get("cinturon",""); activo=request.GET.get("activo",""); rango=request.GET.get("tipo_rango","")
    if cinturon: templates=templates.filter(cinturon_id=cinturon)
    if activo in {"1","0"}: templates=templates.filter(activo=activo=="1")
    if rango: templates=templates.filter(cinturon__tipo_rango=rango)
    return render(request,"alumnos/templates_examen/examen_template_list.html",{"templates":templates,"cinturones":Cinturon.objects.filter(activo=True),"filtros":{"cinturon":cinturon,"activo":activo,"tipo_rango":rango}})

@login_required
def template_create(request):
    form=ExamenTemplateForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=examen_template_service.crear_template(form.cleaned_data); messages.success(request,"Template creado correctamente."); return redirect("alumnos:template_detail",pk=obj.pk)
    return render(request,"alumnos/templates_examen/examen_template_form.html",{"form":form,"modo":"crear"})

@login_required
def template_update(request,pk):
    obj=get_object_or_404(ExamenTemplate.objects.select_related("cinturon"),pk=pk); form=ExamenTemplateForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid():
        try: examen_template_service.actualizar_template(obj,form.cleaned_data)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Template actualizado correctamente."); return redirect("alumnos:template_detail",pk=obj.pk)
    return render(request,"alumnos/templates_examen/examen_template_form.html",{"form":form,"template_examen":obj,"modo":"editar"})

@login_required
def template_duplicar(request,pk):
    obj=get_object_or_404(ExamenTemplate,pk=pk)
    if request.method=="POST":
        nuevo=examen_template_service.duplicar_template(obj); messages.success(request,"Nueva versión del template creada correctamente."); return redirect("alumnos:template_detail",pk=nuevo.pk)
    return redirect("alumnos:template_detail",pk=obj.pk)

@login_required
def template_detail(request,pk):
    obj=get_object_or_404(ExamenTemplate.objects.select_related("cinturon").prefetch_related(Prefetch("secciones",queryset=ExamenTemplateSeccion.objects.order_by("orden").prefetch_related(Prefetch("items",queryset=ExamenTemplateItem.objects.order_by("orden"))))),pk=pk)
    return render(request,"alumnos/templates_examen/examen_template_detail.html",{"template_examen":obj,"template_bloqueado":examen_template_service.template_tiene_examenes_asociados(obj)})

def _estado_template(request,pk,accion,mensaje):
    obj=get_object_or_404(ExamenTemplate,pk=pk)
    if request.method=="POST": accion(obj); messages.success(request,mensaje)
    return redirect("alumnos:template_detail",pk=obj.pk)
@login_required
def template_activar(request,pk): return _estado_template(request,pk,examen_template_service.activar_template,"Template activado correctamente.")
@login_required
def template_desactivar(request,pk): return _estado_template(request,pk,examen_template_service.desactivar_template,"Template desactivado correctamente.")

@login_required
def template_eliminar(request,pk):
    obj=get_object_or_404(ExamenTemplate,pk=pk)
    if request.method=="POST":
        try: examen_template_service.eliminar_template(obj)
        except AlumnosError as exc: mensaje_error_validacion(request,exc); return redirect("alumnos:template_detail",pk=obj.pk)
        messages.success(request,"Template eliminado correctamente.")
    return redirect("alumnos:template_list")

@login_required
def seccion_create(request,template_id):
    obj=get_object_or_404(ExamenTemplate,pk=template_id); form=ExamenTemplateSeccionForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        try: examen_template_service.crear_seccion(obj,form.cleaned_data)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Seccion creada correctamente."); return redirect("alumnos:template_detail",pk=obj.pk)
    return render(request,"alumnos/templates_examen/seccion_form.html",{"form":form,"template_examen":obj})

@login_required
def seccion_update(request,seccion_id):
    obj=get_object_or_404(ExamenTemplateSeccion.objects.select_related("examen_template"),pk=seccion_id); form=ExamenTemplateSeccionForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid():
        try: examen_template_service.actualizar_seccion(obj,form.cleaned_data)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Seccion actualizada correctamente."); return redirect("alumnos:template_detail",pk=obj.examen_template_id)
    return render(request,"alumnos/templates_examen/seccion_form.html",{"form":form,"seccion":obj,"template_examen":obj.examen_template})

@login_required
def seccion_desactivar(request,seccion_id):
    obj=get_object_or_404(ExamenTemplateSeccion,pk=seccion_id)
    if request.method=="POST":
        try: examen_template_service.desactivar_seccion(obj)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Seccion desactivada correctamente.")
    return redirect("alumnos:template_detail",pk=obj.examen_template_id)

@login_required
def item_create(request,seccion_id):
    seccion=get_object_or_404(ExamenTemplateSeccion.objects.select_related("examen_template"),pk=seccion_id); form=ExamenTemplateItemForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        try: examen_template_service.crear_item(seccion,form.cleaned_data)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Item creado correctamente."); return redirect("alumnos:template_detail",pk=seccion.examen_template_id)
    return render(request,"alumnos/templates_examen/item_form.html",{"form":form,"seccion":seccion,"template_examen":seccion.examen_template})

@login_required
def item_update(request,item_id):
    obj=get_object_or_404(ExamenTemplateItem.objects.select_related("seccion","seccion__examen_template"),pk=item_id); form=ExamenTemplateItemForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid():
        try: examen_template_service.actualizar_item(obj,form.cleaned_data)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Item actualizado correctamente."); return redirect("alumnos:template_detail",pk=obj.seccion.examen_template_id)
    return render(request,"alumnos/templates_examen/item_form.html",{"form":form,"item":obj,"seccion":obj.seccion,"template_examen":obj.seccion.examen_template})

@login_required
def item_desactivar(request,item_id):
    obj=get_object_or_404(ExamenTemplateItem.objects.select_related("seccion"),pk=item_id)
    if request.method=="POST":
        try: examen_template_service.desactivar_item(obj)
        except AlumnosError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Item desactivado correctamente.")
    return redirect("alumnos:template_detail",pk=obj.seccion.examen_template_id)
