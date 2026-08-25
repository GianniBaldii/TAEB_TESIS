from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ..forms import ClaseHorarioForm
from ..services import clase_horario_service
from ..services.excepciones import ClasesError
from ._helpers import clase_accesible, horario_accesible, mensaje_error_validacion
@login_required
def horario_create(request, clase_id):
    clase=clase_accesible(request, clase_id); form=ClaseHorarioForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        try: clase_horario_service.crear_horario_clase(clase, form.cleaned_data)
        except ClasesError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request,"Horario agregado correctamente."); return redirect("clases:clase_detail",clase_id=clase.pk)
    return render(request,"clases/horario_form.html",{"form":form,"clase":clase})
@login_required
def horario_update(request, horario_id):
    horario=horario_accesible(request,horario_id); form=ClaseHorarioForm(request.POST or None,instance=horario)
    if request.method=="POST" and form.is_valid():
        try: clase_horario_service.actualizar_horario_clase(horario,form.cleaned_data)
        except ClasesError as exc: mensaje_error_validacion(request,exc)
        else: messages.success(request,"Horario actualizado correctamente."); return redirect("clases:clase_detail",clase_id=horario.clase_id)
    return render(request,"clases/horario_form.html",{"form":form,"clase":horario.clase,"horario":horario})
@login_required
def horario_desactivar(request, horario_id):
    horario=horario_accesible(request,horario_id)
    if request.method=="POST": clase_horario_service.desactivar_horario_clase(horario); messages.success(request,"Horario desactivado correctamente.")
    return redirect("clases:clase_detail",clase_id=horario.clase_id)
