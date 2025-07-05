from django.http import JsonResponse
from applications.doctor.models import CitaMedica

def citamedica_events(request):
    eventos = [
        {
            'title': cita.paciente.nombre_completo,
            'start': f"{cita.fecha}T{cita.hora_cita}",
            'end': f"{cita.fecha}T{cita.hora_cita}",
            'id': cita.id,
        }
        for cita in CitaMedica.objects.select_related('paciente').all()
    ]
    return JsonResponse(eventos, safe=False)
