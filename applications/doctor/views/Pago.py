from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect , get_object_or_404
import requests
from django.conf import settings

from applications.doctor.models import Pago, DetallePago
from applications.doctor.forms.Pago import PagoForm, DetallePagoFormSet
from applications.doctor.utils.pago import EstadoPagoChoices

# Agrega la importación del SDK de PayPal
import paypalrestsdk

# Configura el SDK de PayPal (puedes poner esto en settings.py y solo importar aquí)
paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a "live" en producción
    "client_id": getattr(settings, "PAYPAL_CLIENT_ID", "ARC176RU_02YfD-NA_uHAYXpXjo0si03zsegvrJIiKQd9A24axcY5Ml0V1ywB6uqqnaVHTDBPVHLln6d"),
    "client_secret": getattr(settings, "PAYPAL_CLIENT_SECRET", "EIJw7l9-51vtTj3jP36DJL925JkWnbXGf3juKaBRgnZRURAw1RPaaWgBkGS_KGK9Fhdf6LDpuvDiAZn_")
})

class PagoCreateView(CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'doctor/pagos/form.html'
    success_url = reverse_lazy('doctor:pago_list')  # Cambia esto según tu url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalle_formset'] = DetallePagoFormSet(self.request.POST, self.request.FILES)
        else:
            context['detalle_formset'] = DetallePagoFormSet()
        context['grabar'] = 'Registrar Pago'
        context['back_url'] = self.success_url
        context['es_edicion'] = False
        context['estado_pago'] = ''
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context['detalle_formset']
        metodo_pago = form.cleaned_data.get('metodo_pago')
        paypal_transaction_id = self.request.POST.get('paypal_transaction_id')
        # Si el método de pago es PayPal, forzar estado a pagado
        if metodo_pago == 'paypal':
            form.instance.estado = EstadoPagoChoices.PAGADO
        # Validar pago PayPal si corresponde
        if metodo_pago == 'paypal':
            if not paypal_transaction_id:
                messages.error(self.request, "No se recibió el ID de la transacción de PayPal.")
                return self.form_invalid(form)
            # Validar la orden de PayPal usando la API REST v2
            try:
                # Obtener token de acceso
                auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
                data = {'grant_type': 'client_credentials'}
                token_resp = requests.post(
                    'https://api-m.sandbox.paypal.com/v1/oauth2/token',
                    data=data,
                    auth=auth
                )
                token_resp.raise_for_status()
                access_token = token_resp.json()['access_token']
                # Consultar la orden
                headers = {'Authorization': f'Bearer {access_token}'}
                order_resp = requests.get(
                    f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_transaction_id}',
                    headers=headers
                )
                order_resp.raise_for_status()
                order_data = order_resp.json()
                if order_data['status'] not in ['COMPLETED', 'APPROVED']:
                    messages.error(self.request, "El pago de PayPal no fue aprobado.")
                    return self.form_invalid(form)
            except Exception as e:
                messages.error(self.request, f"Error validando el pago de PayPal: {str(e)}")
                return self.form_invalid(form)
        try:
            with transaction.atomic():
                self.object = form.save()
                if detalle_formset.is_valid():
                    detalles = detalle_formset.save(commit=False)
                    for detalle in detalles:
                        detalle.pago = self.object
                        detalle.save()
                    detalle_formset.save_m2m()
                    # Si no hay detalles, el monto total será 0
                    self.object.monto_total = sum([d.subtotal for d in self.object.detalles.all()]) if detalles else 0
                    self.object.save()
                else:
                    return self.form_invalid(form)
                messages.success(self.request, "Pago registrado exitosamente.")
                return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error al registrar el pago: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)
    
class PagoUpdateView(UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'doctor/pagos/form.html'
    success_url = reverse_lazy('doctor:pago_list')  # Cambia esto según tu url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['detalle_formset'] = DetallePagoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['detalle_formset'] = DetallePagoFormSet(instance=self.object)
        context['grabar'] = 'Actualizar Pago'
        context['back_url'] = self.success_url
        context['es_edicion'] = True
        context['estado_pago'] = self.object.estado if self.object else ''
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context['detalle_formset']
        try:
            with transaction.atomic():
                self.object = form.save()
                if detalle_formset.is_valid():
                    detalles = detalle_formset.save(commit=False)
                    for detalle in detalles:
                        detalle.pago = self.object
                        detalle.save()
                    detalle_formset.save_m2m()
                    # Elimina los detalles marcados para borrar
                    for obj in detalle_formset.deleted_objects:
                        obj.delete()
                    # Actualiza el monto total del pago sumando los subtotales
                    self.object.monto_total = sum([d.subtotal for d in self.object.detalles.all()])
                    self.object.save()
                else:
                    return self.form_invalid(form)
                messages.success(self.request, "Pago actualizado exitosamente.")
                return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Error al actualizar el pago: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)
    
class PagoListView(ListView):
    model = Pago
    template_name = 'doctor/pagos/list.html'
    context_object_name = 'pagos'
    paginate_by = 5  # Puedes ajustar la cantidad por página

    def get_queryset(self):
        return Pago.objects.select_related('atencion').order_by('-fecha_pago', '-id')

class PagoDeleteView(DeleteView):
    model = Pago
    template_name = 'doctor/pagos/confirm_delete.html'
    success_url = reverse_lazy('doctor:pago_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Pago eliminado correctamente.")
        return super().delete(request, *args, **kwargs)