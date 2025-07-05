from django import forms
from applications.doctor.models import ServiciosAdicionales
from django.forms import ModelForm

class ServiciosAdicionalesForm(ModelForm):
    class Meta:
        model = ServiciosAdicionales
        fields = ['nombre_servicio', 'costo_servicio', 'descripcion', 'activo']
        widgets = {
            'nombre_servicio': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-pastel-blue-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pastel-purple-200'
            }),
            'costo_servicio': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-pastel-blue-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pastel-purple-200',
                'step': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-pastel-blue-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pastel-purple-200',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }