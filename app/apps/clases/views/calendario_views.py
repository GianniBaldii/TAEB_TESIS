from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from apps.escuelas.models import Escuela, EscuelaDocente
from ..forms import ClaseExtraForm
from ..services import clase_horario_service, clase_sesion_service
from ..services.excepciones import ClasesError
from ._helpers import clase_accesible, clase_queryset, escuelas_visibles, horario_accesible, mensaje_error_validacion, rango_calendario

@login_required
def calendario(request):
    fecha_desde,fecha_hasta,vista=rango_calendario(request); escuela_id=request.GET.get("escuela",""); clase_id=request.GET.get("clase",""); docente_id=request.GET.get("docente","")
    escuelas=escuelas_visibles(request)
    if request.user.is_superuser and escuela_id: escuelas=escuelas.filter(pk=escuela_id)
    clases=clase_queryset(request).filter(escuela__in=escuelas,activo=True)
    docentes=EscuelaDocente.objects.select_related("docente__usuario","escuela").filter(escuela__in=escuelas,activo=True,docente__activo=True)
    ocurrencias=[]; sesiones=[]
    for escuela in escuelas:
        ocurrencias.extend(clase_horario_service.obtener_ocurrencias_calendario(escuela,fecha_desde,fecha_hasta)); sesiones.extend(clase_sesion_service.obtener_sesiones_calendario(escuela,fecha_desde,fecha_hasta))
    if clase_id:
        ocurrencias=[o for o in ocurrencias if str(o["clase"].pk)==clase_id]; sesiones=[s for s in sesiones if str(s.clase_id)==clase_id]
    if docente_id:
        ocurrencias=[o for o in ocurrencias if str(o["clase"].docente_responsable_id)==docente_id]; sesiones=[s for s in sesiones if str(s.docente_a_cargo_id or s.clase.docente_responsable_id)==docente_id]
    claves={(s.clase_id,s.fecha,s.hora_inicio):s for s in sesiones}; eventos=[o for o in ocurrencias if (o["clase"].pk,o["fecha"],o["hora_inicio"]) not in claves]
    eventos.extend({"tipo":"sesion","sesion":s} for s in sesiones); eventos=sorted(eventos,key=lambda x:(x["sesion"].fecha if x["tipo"]=="sesion" else x["fecha"],x["sesion"].hora_inicio if x["tipo"]=="sesion" else x["hora_inicio"]))
    return render(request,"clases/calendario.html",{"eventos":eventos,"fecha_desde":fecha_desde,"fecha_hasta":fecha_hasta,"fecha_anterior":fecha_desde-timedelta(days=1 if vista=="dia" else 7),"fecha_siguiente":fecha_hasta+timedelta(days=1),"vista":vista,"escuelas":Escuela.objects.filter(activo=True) if request.user.is_superuser else [],"clases":clases,"docentes":docentes,"filtros":{"escuela":escuela_id,"clase":clase_id,"docente":docente_id}})

@login_required
def abrir_ocurrencia(request,horario_id):
    horario=horario_accesible(request,horario_id); fecha=parse_date(request.GET.get("fecha",""))
    if not fecha: mensaje_error_validacion(request,"Fecha invalida para abrir la sesion."); return redirect("clases:calendario")
    try: sesion=clase_sesion_service.crear_o_obtener_sesion(horario.clase,horario,fecha)
    except ClasesError as exc: mensaje_error_validacion(request,exc); return redirect("clases:calendario")
    return redirect("clases:sesion_detail",sesion_id=sesion.pk)

@login_required
def clase_extra_create(request,clase_id):
    clase=clase_accesible(request,clase_id); form=ClaseExtraForm(request.POST or None,escuela=clase.escuela)
    if request.method=="POST" and form.is_valid():
        try: sesion=clase_sesion_service.crear_clase_extra(clase=clase,fecha=form.cleaned_data["fecha"],hora_inicio=form.cleaned_data["hora_inicio"],hora_fin=form.cleaned_data["hora_fin"],docente_a_cargo=form.cleaned_data["docente_a_cargo"],observaciones=form.cleaned_data["observaciones"])
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Clase extra creada correctamente."); return redirect("clases:sesion_detail",sesion_id=sesion.pk)
    return render(request,"clases/clase_extra_form.html",{"form":form,"clase":clase})
