from django import forms
from django.forms import ModelForm
from applications.doctor.models import HorarioAtencion

class HorarioAtencionForm(ModelForm):
    class Meta:
        model = HorarioAtencion
        fields = '__all__'
        widgets = {
            'dia_semana': forms.Select(attrs={
                'class': 'form-select w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'type': 'time'
            }),
            'intervalo_desde': forms.TimeInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'type': 'time'
            }),
            'intervalo_hasta': forms.TimeInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-300 focus:ring focus:ring-blue-200',
                'type': 'time'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'dia_semana':
                self.fields[field].required = False
            else:
                self.fields[field].required = True
        self.fields['activo'].initial = False