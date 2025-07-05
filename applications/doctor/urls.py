from django.urls import path


from applications.doctor.views.HorarioAtencion import HorarioAtencionCreateView, HorarioAtencionListView,HorarioAtencionUpdateView, HorarioAtencionDeleteView
from applications.doctor.views.atencion_medica import (
    AtencionListView, AtencionCreateView, AtencionUpdateView,
    AtencionDeleteView
)
from applications.doctor.views.citamedica import CitaMedicaListView, CitaMedicaCreateView, CitaMedicaUpdateView, CitaMedicaDeleteView
from applications.doctor.views.citamedica_api import citamedica_events
from applications.doctor.views.crear_paciente import CrearPacienteView 
from applications.doctor.views.Pago import PagoCreateView, PagoUpdateView, PagoListView, Pago, PagoDeleteView
from applications.doctor.views.ServiciosAdicionales import ServiciosAdicionalesCreateView, ServiciosAdicionalesUpdateView, ServiciosAdicionalesListView, ServiciosAdicionalesDeleteView, servicio_adicional_create_api
from applications.doctor.views.crear_paciente import CrearPacienteView, lista_pacientes_api



app_name = 'doctor'

urlpatterns = [
    # Rutas para vistas relacionadas con Doctor
    path('atencion_list/', AtencionListView.as_view(), name="atencion_list"),
    path('atencion_create/', AtencionCreateView.as_view(), name="atencion_create"),
    path('atencion_update/<int:pk>/', AtencionUpdateView.as_view(), name="atencion_update"),
    path('atencion_delete/<int:pk>/', AtencionDeleteView.as_view(), name="atencion_delete"),

    # Ruta nueva para guardar paciente desde JS
    path('crear_paciente/', CrearPacienteView.as_view(), name='crear_paciente'),
    path('api/pacientes/', CrearPacienteView.as_view(), name='crear_paciente'),
    path('api/pacientes/lista/', lista_pacientes_api, name='lista_pacientes_api'),

    

    # Rutas para Horario de Atención
    path('horarioatencion_list/', HorarioAtencionListView.as_view(), name="horarioatencion_list"),
    path('horarioatencion_create/', HorarioAtencionCreateView.as_view(), name="horarioatencion_create"),
    path('horarioatencion_update/<int:pk>/', HorarioAtencionUpdateView.as_view(), name="horarioatencion_update"),
    path('horarioatencion_delete/<int:pk>/', HorarioAtencionDeleteView.as_view(), name="horarioatencion_delete"),

    path('pago_list/', PagoListView.as_view(), name="pago_list"),
    path('pago_create/', PagoCreateView.as_view(), name="pago_create"),
    path('pago_update/<int:pk>/', PagoUpdateView.as_view(), name="pago_update"),
    path('pago_delete/<int:pk>/', PagoDeleteView.as_view(), name="pago_delete"),

    path('servicios/api/nuevo/', servicio_adicional_create_api, name='servicio_adicional_create_api'),
    path('servicio_adicional_create/', ServiciosAdicionalesCreateView.as_view(), name="servicio_adicional_create"),
    path('servicio_adicional_update/<int:pk>/', ServiciosAdicionalesUpdateView.as_view(), name="servicio_adicional_update"),
    path('servicio_adicional_list/', ServiciosAdicionalesListView.as_view(), name="servicio_adicional_list"),
    path('servicio_adicional_delete/<int:pk>/', ServiciosAdicionalesDeleteView.as_view(), name="servicio_adicional_delete"),

        # CRUD CitaMedica
    path('citamedica/', CitaMedicaListView.as_view(), name="citamedica_list"),
    path('citamedica/create/', CitaMedicaCreateView.as_view(), name="citamedica_create"),
    path('citamedica/update/<int:pk>/', CitaMedicaUpdateView.as_view(), name="citamedica_update"),
    path('citamedica/delete/<int:pk>/', CitaMedicaDeleteView.as_view(), name="citamedica_delete"),
    path('citamedica/events/', citamedica_events, name="citamedica_events"),

]
