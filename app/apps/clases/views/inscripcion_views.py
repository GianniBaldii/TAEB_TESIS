from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import ClaseAlumnoForm
from ..models import ClaseAlumno
from ..services import clase_alumno_service, clase_service
from ..services.excepciones import ClasesError
from ._helpers import clase_accesible, mensaje_error_validacion
@login_required
def clase_alumno_create(request,clase_id):
    clase=clase_accesible(request,clase_id); alumnos=clase_alumno_service.obtener_alumnos_disponibles_para_clase(clase,request.GET.get("q","").strip()); form=ClaseAlumnoForm(request.POST or None,alumnos_queryset=alumnos)
    if request.method=="POST" and form.is_valid():
        try: clase_alumno_service.inscribir_alumno_en_clase(clase,form.cleaned_data["alumno_escuela"],form.cleaned_data["observaciones"])
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Alumno inscripto correctamente."); return redirect("clases:clase_detail",clase_id=clase.pk)
    return render(request,"clases/clase_alumno_form.html",{"form":form,"clase":clase,"busqueda":request.GET.get("q","")})
def _inscripcion(request,pk):
    obj=get_object_or_404(ClaseAlumno.objects.select_related("clase","clase__escuela","alumno_escuela","alumno_escuela__alumno"),pk=pk); clase_service.validar_acceso_clase(request.user,obj.clase); return obj
@login_required
def clase_alumno_baja(request,clase_alumno_id):
    obj=_inscripcion(request,clase_alumno_id)
    if request.method=="POST": clase_alumno_service.dar_baja_alumno_de_clase(obj); messages.success(request,"Alumno dado de baja de la clase.")
    return redirect("clases:clase_detail",clase_id=obj.clase_id)
@login_required
def clase_alumno_reactivar(request,clase_alumno_id):
    obj=_inscripcion(request,clase_alumno_id)
    if request.method=="POST":
        try: clase_alumno_service.reactivar_alumno_en_clase(obj)
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Inscripcion reactivada correctamente.")
    return redirect("clases:clase_detail",clase_id=obj.clase_id)
