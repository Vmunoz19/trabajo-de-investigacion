from django import forms
from django.forms import ModelForm, inlineformset_factory, BaseInlineFormSet
from applications.doctor.models import Pago, DetallePago


class PagoForm(ModelForm):
    class Meta:
        model = Pago
        fields = [
            'atencion',
            'metodo_pago',
            'monto_total',
            'estado',
            'nombre_pagador',
            'referencia_externa',
            'evidencia_pago',
            'observaciones',
            'activo',
        ]
        widgets = {
            'atencion': forms.Select(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'monto_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'nombre_pagador': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia_externa': forms.TextInput(attrs={'class': 'form-control'}),
            'evidencia_pago': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo_pago')
        referencia = cleaned_data.get('referencia_externa')

        if metodo == 'PAYPAL' and not referencia:
            self.add_error('referencia_externa', 'La referencia externa es obligatoria si el método de pago es PayPal.')
        return cleaned_data

# Formset para los detalles de pago (servicios adicionales)
class RequiredIfFilledDetallePagoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            # Considerar la fila vacía si todos los campos principales están vacíos
            cleaned = form.cleaned_data if hasattr(form, 'cleaned_data') else {}
            servicio = cleaned.get('servicio_adicional')
            cantidad = cleaned.get('cantidad')
            precio = cleaned.get('precio_unitario')
            descuento = cleaned.get('descuento_porcentaje')
            aplica_seguro = cleaned.get('aplica_seguro')
            valor_seguro = cleaned.get('valor_seguro')
            descripcion_seguro = cleaned.get('descripcion_seguro')
            # Si todos los campos principales están vacíos, ignorar validación de requeridos
            if not (servicio or cantidad or precio or descuento or aplica_seguro or valor_seguro or descripcion_seguro):
                form.cleaned_data['DELETE'] = True  # Marca para que Django ignore esta fila
                continue
            # Si algún campo principal está lleno, dejar que Django valide normalmente

DetallePagoFormSet = inlineformset_factory(
    Pago,
    DetallePago,
    formset=RequiredIfFilledDetallePagoFormSet,
    fields=[
        'servicio_adicional',
        'cantidad',
        'precio_unitario',
        'descuento_porcentaje',
        'aplica_seguro',
        'valor_seguro',
        'descripcion_seguro',
    ],
    extra=1,
    can_delete=True,
    widgets={
        'servicio_adicional': forms.Select(attrs={'class': 'form-control'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        'descuento_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        'aplica_seguro': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'valor_seguro': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        'descripcion_seguro': forms.TextInput(attrs={'class': 'form-control'}),
    }
)