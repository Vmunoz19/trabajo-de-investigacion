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
    template_name = 'doctor/horario_atencion/form.html'
    permission_required = 'add_horarioatencion'
    success_url = reverse_lazy('doctor:horarioatencion_list')

    def get(self, request, *args, **kwargs):
        # Un formulario por cada día de la semana, con prefijos únicos
        forms = []
        for dia, _ in DiaSemanaChoices.choices:
            forms.append({
                'dia': dia,
                'form': HorarioAtencionForm(prefix=dia, initial={'dia_semana': dia})
            })
        return render(request, self.template_name, {
            'forms': forms,
            'grabar': 'Grabar Horarios',
            'back_url': self.success_url
        })

    def post(self, request, *args, **kwargs):
        forms = []
        success = True
        with transaction.atomic():
            for dia, _ in DiaSemanaChoices.choices:
                form = HorarioAtencionForm(request.POST, prefix=dia)
                forms.append({'dia': dia, 'form': form})
                # Solo guardar si tiene hora_inicio y hora_fin y es válido
                if form.is_valid() and form.cleaned_data.get('hora_inicio') and form.cleaned_data.get('hora_fin'):
                    form.save()
                else:
                    # Si algún formulario no es válido, no guardar nada
                    success = False
        if success:
            messages.success(request, "Horarios guardados correctamente.")
            return redirect(self.success_url)
        else:
            messages.error(request, "Corrija los errores en el formulario.")
            return render(request, self.template_name, {
                'forms': forms,
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
        messages.error(self.request, "Corrija los errores en el formulario.")
        print("Errores en el formulario:", form.errors)
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