from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from applications.doctor.models import ServiciosAdicionales
from applications.doctor.forms.ServiciosAdicionales import ServiciosAdicionalesForm

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from applications.doctor.models import ServiciosAdicionales


class ServiciosAdicionalesCreateView(CreateView):
    model = ServiciosAdicionales
    form_class = ServiciosAdicionalesForm
    template_name = 'doctor/serviciosadicionales/form.html'
    success_url = reverse_lazy('doctor:servicio_adicional_list')

    def form_valid(self, form):
        messages.success(self.request, "Servicio adicional creado correctamente.")
        return super().form_valid(form)

class ServiciosAdicionalesUpdateView(UpdateView):
    model = ServiciosAdicionales
    form_class = ServiciosAdicionalesForm
    template_name = 'doctor/serviciosadicionales/form.html'
    success_url = reverse_lazy('doctor:servicio_adicional_list')

    def form_valid(self, form):
        messages.success(self.request, "Servicio adicional actualizado correctamente.")
        return super().form_valid(form)

class ServiciosAdicionalesListView(ListView):
    model = ServiciosAdicionales
    template_name = 'doctor/serviciosadicionales/list.html'
    context_object_name = 'servicios'
    queryset = ServiciosAdicionales.objects.order_by('nombre_servicio')

class ServiciosAdicionalesDeleteView(DeleteView):
    model = ServiciosAdicionales
    template_name = 'doctor/serviciosadicionales/confirm_delete.html'
    success_url = reverse_lazy('doctor:servicio_adicional_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Servicio adicional eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

@csrf_exempt
def servicio_adicional_create_api(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre_servicio")
        costo = request.POST.get("costo_servicio")
        descripcion = request.POST.get("descripcion")
        if nombre and costo:
            servicio = ServiciosAdicionales.objects.create(
                nombre_servicio=nombre,
                costo_servicio=costo,
                descripcion=descripcion,
                activo=True
            )
            return JsonResponse({"id": servicio.id, "nombre_servicio": servicio.nombre_servicio})
    return JsonResponse({"error": "Datos inválidos"}, status=400)