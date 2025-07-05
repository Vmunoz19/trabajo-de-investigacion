from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from applications.core.models import Paciente
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from datetime import datetime
from django.views.decorators.http import require_GET

@method_decorator(csrf_exempt, name='dispatch')
class CrearPacienteView(View):
    def get(self, request):
        return render(request, 'core/paciente/form.html')
    def post(self, request):
        try:
            data = request.POST
            files = request.FILES

            paciente = Paciente(
                nombres=data.get('nombres', ''),
                apellidos=data.get('apellidos', ''),
                cedula_ecuatoriana=data.get('cedula_ecuatoriana', ''),
                fecha_nacimiento=datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d').date(),
                telefono=data.get('telefono'),
                email=data.get('email'),
                sexo=data.get('sexo'),
                estado_civil=data.get('estado_civil'),
                direccion=data.get('direccion'),
                latitud=data.get('latitud') or None,
                longitud=data.get('longitud') or None,
                tipo_sangre_id=data.get('tipo_sangre') or None,
                antecedentes_personales=data.get('antecedentes_personales'),
                antecedentes_quirurgicos=data.get('antecedentes_quirurgicos'),
                antecedentes_familiares=data.get('antecedentes_familiares'),
                alergias=data.get('alergias'),
                medicamentos_actuales=data.get('medicamentos_actuales'),
                habitos_toxicos=data.get('habitos_toxicos'),
                vacunas=data.get('vacunas'),
                antecedentes_gineco_obstetricos=data.get('antecedentes_gineco_obstetricos'),
                activo=True,
                foto=files.get('foto')  # ⚠️ Importante: asegúrate de manejar la imagen
            )

            paciente.full_clean()
            paciente.save()

            return JsonResponse({
                'status': 'success',
                'paciente': model_to_dict(paciente)
            }, status=201)

        except ValidationError as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)

@require_GET
def lista_pacientes_api(request):
    pacientes = Paciente.objects.filter(activo=True).order_by('-id')
    data = []
    for p in pacientes:
        data.append({
            'id': p.id,
            'nombres': p.nombres,
            'apellidos': p.apellidos,
            'cedula_ecuatoriana': p.cedula_ecuatoriana,
        })
    return JsonResponse(data, safe=False)
