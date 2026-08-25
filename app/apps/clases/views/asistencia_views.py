from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ..forms import CancelarSesionForm
from ..models import AsistenciaClase
from ..services import asistencia_service, clase_sesion_service
from ..services.excepciones import ClasesError
from ._helpers import mensaje_error_validacion, sesion_accesible

@login_required
def sesion_detail(request,sesion_id):
    sesion=sesion_accesible(request,sesion_id)
    return render(request,"clases/sesion_detail.html",{"sesion":sesion,"resumen":asistencia_service.obtener_resumen_asistencia_sesion(sesion)})
@login_required
def asistencia_form(request,sesion_id):
    sesion=sesion_accesible(request,sesion_id)
    if request.method=="POST":
        datos={}
        for clave,valor in request.POST.items():
            if clave.startswith("estado_"):
                aid=clave.replace("estado_",""); datos[aid]={"estado":valor,"observaciones":request.POST.get(f"observaciones_{aid}","")}
        try: asistencia_service.guardar_asistencias_sesion(sesion,datos,request.user)
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Asistencia guardada correctamente."); return redirect("clases:asistencia_form",sesion_id=sesion.pk)
    try: asistencias=asistencia_service.inicializar_asistencias_sesion(sesion,request.user)
    except ClasesError as exc:
        mensaje_error_validacion(request,exc); asistencias=sesion.asistencias.select_related("clase_alumno__alumno_escuela__alumno","clase_alumno__alumno_escuela__alumno__cinturon_actual")
    return render(request,"clases/asistencia_form.html",{"sesion":sesion,"asistencias":asistencias,"estados":AsistenciaClase.Estado.choices})
def _accion(request,sesion_id,accion,mensaje,destino):
    sesion=sesion_accesible(request,sesion_id)
    if request.method=="POST":
        try: accion(sesion,request.user)
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,mensaje)
    return redirect(destino,sesion_id=sesion.pk)
@login_required
def marcar_todos_presentes(request,sesion_id): return _accion(request,sesion_id,asistencia_service.marcar_todos_presentes,"Todos los alumnos fueron marcados presentes.","clases:asistencia_form")
@login_required
def cerrar_asistencia(request,sesion_id): return _accion(request,sesion_id,asistencia_service.cerrar_asistencia_sesion,"Asistencia cerrada correctamente.","clases:sesion_detail")
@login_required
def reabrir_asistencia(request,sesion_id): return _accion(request,sesion_id,asistencia_service.reabrir_asistencia_sesion,"Asistencia reabierta correctamente.","clases:asistencia_form")
@login_required
def cancelar_sesion(request,sesion_id):
    sesion=sesion_accesible(request,sesion_id); form=CancelarSesionForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        try: clase_sesion_service.cancelar_sesion(sesion,form.cleaned_data["motivo"])
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Sesion cancelada correctamente."); return redirect("clases:sesion_detail",sesion_id=sesion.pk)
    return render(request,"clases/cancelar_sesion_form.html",{"form":form,"sesion":sesion})
