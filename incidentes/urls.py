from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/incidentes', views.IncidenteViewSet)
router.register(r'api/dispositivos', views.DispositivoViewSet)

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Incidentes
    path('nuevo-incidente/', views.nuevo_incidente, name='nuevo_incidente'),
    path('cerrar-incidente/<int:incidente_id>/', views.cerrar_incidente, name='cerrar_incidente'),
    
    # Móviles
    path('actualizar-movil/<int:movil_id>/', views.actualizar_estado_movil, name='actualizar_estado_movil'),
    
    # APIs auxiliares
    path('api/autocomplete/direcciones/', views.autocomplete_direcciones, name='autocomplete_direcciones'),
    path('api/geocoding/coordenadas/', views.obtener_coordenadas, name='obtener_coordenadas'),
    path('api/iot/comandos/', views.iot_comandos, name='iot_comandos'),
    path('api/iot/accion/', views.iot_accion, name='iot_accion'),
    
    # Control de hardware simple
    path('control-hardware/', views.control_hardware, name='control_hardware'),
    path('control-simple/', views.control_simple, name='control_simple'),
    path('api/comando-mqtt/', views.enviar_comando_mqtt, name='enviar_comando_mqtt'),
    path('api/comando-simple/', views.comando_simple, name='comando_simple'),
    
    # API REST
    path('', include(router.urls)),
]