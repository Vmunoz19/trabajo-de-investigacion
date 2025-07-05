from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from applications.doctor.models import CitaMedica

class CitaMedicaListView(ListView):
    model = CitaMedica
    template_name = 'doctor/citamedica/citamedica_list.html'
    context_object_name = 'citas'


    


class CitaMedicaCreateView(CreateView):
    model = CitaMedica
    template_name = 'doctor/citamedica/citamedica_form.html'
    fields = ['paciente', 'fecha', 'hora_cita', 'estado', 'observaciones']
    success_url = reverse_lazy('doctor:citamedica_list')

    def form_valid(self, form):
        paciente = form.cleaned_data['paciente']
        fecha = form.cleaned_data['fecha']
        hora_cita = form.cleaned_data['hora_cita']
        if CitaMedica.objects.filter(paciente=paciente, fecha=fecha, hora_cita=hora_cita).exists():
            form.add_error(None, 'Ya existe una cita para este paciente en la fecha y hora seleccionadas.')
            return self.form_invalid(form)
        messages.success(self.request, 'Cita médica creada exitosamente.')
        return super().form_valid(form)

class CitaMedicaUpdateView(UpdateView):
    model = CitaMedica
    template_name = 'doctor/citamedica/citamedica_form.html'
    fields = ['paciente', 'fecha', 'hora_cita', 'estado', 'observaciones']
    success_url = reverse_lazy('doctor:citamedica_list')

    def form_valid(self, form):
        paciente = form.cleaned_data['paciente']
        fecha = form.cleaned_data['fecha']
        hora_cita = form.cleaned_data['hora_cita']
        if CitaMedica.objects.filter(paciente=paciente, fecha=fecha, hora_cita=hora_cita).exclude(pk=self.object.pk).exists():
            form.add_error(None, 'Ya existe una cita para este paciente en la fecha y hora seleccionadas.')
            return self.form_invalid(form)
        messages.success(self.request, 'Cita médica actualizada exitosamente.')
        return super().form_valid(form)

class CitaMedicaDeleteView(DeleteView):
    model = CitaMedica
    template_name = 'doctor/citamedica/citamedica_confirm_delete.html'
    success_url = reverse_lazy('doctor:citamedica_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Cita médica eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
