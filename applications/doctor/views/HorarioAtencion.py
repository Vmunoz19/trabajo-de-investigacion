from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db import transaction
from django.shortcuts import redirect, render
from django.db.models import Q
from applications.doctor.models import HorarioAtencion
from applications.doctor.forms.HorarioAtencion import HorarioAtencionForm
from applications.security.components.mixin_crud import (
    CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
)
from applications.doctor.utils.doctor import DiaSemanaChoices

class HorarioAtencionListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'doctor/horario_atencion/list.html'
    model = HorarioAtencion
    context_object_name = 'horarios'
    permission_required = 'view_horarioatencion'

    def get_queryset(self):
        # Ordenar por día de la semana
        return self.model.objects.all().order_by('dia_semana', 'hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('doctor:horarioatencion_create')
        # Agrupar por día de la semana para mostrar en la vista
        dias = {dia[0]: [] for dia in DiaSemanaChoices.choices}
        for horario in context['horarios']:
            dias[horario.dia_semana].append(horario)
        context['dias'] = dias
        return context

class HorarioAtencionCreateView(PermissionMixin, CreateView):
    model = HorarioAtencion
    template_name = 'doctor/horario_atencion/form.html'
    permission_required = 'add_horarioatencion'
    success_url = reverse_lazy('doctor:horarioatencion_list')
    

    def get(self, request, *args, **kwargs):
        forms = []
        horarios_existentes = {h.dia_semana: h for h in self.get_queryset()}

        for dia, _ in DiaSemanaChoices.choices:
            if dia in horarios_existentes:
                # Ya hay un horario registrado para este día → precargar el formulario
                instance = horarios_existentes[dia]
                form = HorarioAtencionForm(prefix=dia, instance=instance)
            else:
                # No hay horario registrado → formulario vacío con el día preestablecido
                form = HorarioAtencionForm(prefix=dia, initial={'dia_semana': dia})

            forms.append({'dia': dia, 'form': form})

        return render(request, self.template_name, {
            'forms': forms,
            'horarios_existentes': horarios_existentes.values(),
            'grabar': 'Grabar Horarios',
            'back_url': self.success_url
        })

    def post(self, request, *args, **kwargs):
        forms = []
        success = True
        guardado_alguno = False

        with transaction.atomic():
            for dia, _ in DiaSemanaChoices.choices:
                form = HorarioAtencionForm(request.POST, prefix=dia)
                forms.append({'dia': dia, 'form': form})

                # Verifica si se ingresaron valores para ese día
                tiene_datos = request.POST.get(f"{dia}-hora_inicio") and request.POST.get(f"{dia}-hora_fin")

                if tiene_datos:
                    if form.is_valid():
                        cd = form.cleaned_data
                        HorarioAtencion.objects.update_or_create(
                            dia_semana=cd['dia_semana'],
                            hora_inicio=cd['hora_inicio'],
                            hora_fin=cd['hora_fin'],
                            defaults={
                                'intervalo_desde': cd.get('intervalo_desde'),
                                'intervalo_hasta': cd.get('intervalo_hasta'),
                                'activo': cd.get('activo'),
                            }
                        )
                        guardado_alguno = True
                    else:
                        success = False  # Un formulario con datos pero inválido → marcar error

        if success and guardado_alguno:
            messages.success(request, "Horarios guardados o actualizados correctamente.")
            return redirect(self.success_url)
        else:
            if not guardado_alguno:
                messages.error(request, "No se ingresaron datos válidos para guardar.")
            else:
                messages.error(request, "Corrija los errores en los formularios.")
            return render(request, self.template_name, {
                'forms': forms,
                'horarios_existentes': self.get_queryset(),
                'grabar': 'Grabar Horarios',
                'back_url': self.success_url
            })

        
class HorarioAtencionUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = HorarioAtencion
    template_name = 'doctor/horario_atencion/form_single.html'
    form_class = HorarioAtencionForm
    success_url = reverse_lazy('doctor:horarioatencion_list')
    permission_required = 'change_horarioatencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar Horario'
        context['back_url'] = self.success_url
        return context

    def form_invalid(self, form):
        print("Errores en formulario de actualización:", form.errors)
        messages.error(self.request, "Corrija los errores en el formulario.")
        return super().form_invalid(form)

class HorarioAtencionDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = HorarioAtencion
    template_name = 'doctor/horario_atencion/delete.html'
    success_url = reverse_lazy('doctor:horarioatencion_list')
    permission_required = 'delete_horarioatencion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Eliminar Horario'
        context['description'] = f"¿Desea eliminar el horario de {self.object.get_dia_semana_display()}?"
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Horario eliminado correctamente.")
        return response