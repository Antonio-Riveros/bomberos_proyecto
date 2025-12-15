from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from .models import Incidente, AccionIoT, Dispositivo, Movil, Llamada
from .serializers import IncidenteSerializer, AccionIoTSerializer, DispositivoSerializer, MovilSerializer

# Vista principal del dashboard
def dashboard(request):
    # Si el usuario está autenticado, mostrar dashboard
    if request.user.is_authenticated:
        ahora = timezone.now()
        
        # Última llamada
        ultima_llamada = Llamada.objects.order_by('-fecha_hora').first() if Llamada.objects.exists() else None
        
        # Historial reciente (últimas 24 horas)
        historial_reciente = Incidente.objects.filter(
            fecha_registro__gte=ahora - timedelta(hours=24)
        ).order_by('-fecha_registro')[:10]
        
        # Móviles disponibles
        moviles = Movil.objects.all().order_by('numero')
        
        # Estadísticas
        total_incidentes = Incidente.objects.count()
        incidentes_hoy = Incidente.objects.filter(
            fecha_registro__date=ahora.date()
        ).count()
        moviles_activos = Movil.objects.filter(estado='EN_SERVICIO').count()
        
        context = {
            'ultima_llamada': ultima_llamada,
            'historial_reciente': historial_reciente,
            'moviles': moviles,
            'total_incidentes': total_incidentes,
            'incidentes_hoy': incidentes_hoy,
            'moviles_activos': moviles_activos,
            'hora_actual': ahora.strftime("%d/%m %H:%M"),
            'user': request.user,
        }
        
        return render(request, 'index.html', context)
    else:
        # Si no está autenticado, redirigir a login
        return redirect('/admin/login/?next=/')

# Vista para crear nuevo incidente
@login_required
def nuevo_incidente(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            tipo_incidente = request.POST.get('tipo_incidente')
            direccion = request.POST.get('direccion')
            detalles = request.POST.get('detalles')
            toque_sirena = request.POST.get('toque_sirena') == 'on'
            
            # Crear incidente
            incidente = Incidente.objects.create(
                tipo=tipo_incidente,
                direccion=direccion,
                detalles=detalles,
                prioridad_alta=toque_sirena,
                estado='ASIGNADO',
                operador=request.user,
                fecha_registro=timezone.now()
            )
            
            # Si hay toque de sirena, activar acciones IoT
            if toque_sirena:
                # Crear acción para activar sirenas
                sirenas = Dispositivo.objects.filter(tipo='SIRENA')
                for sirena in sirenas:
                    AccionIoT.objects.create(
                        incidente=incidente,
                        dispositivo=sirena,
                        tipo='EMERGENCIA',
                        accion='ACTIVAR',
                        detalles={
                            'incidente_id': incidente.id,
                            'prioridad': 'ALTA',
                            'mensaje': f'Incidente {incidente.id} - {tipo_incidente}'
                        },
                        timestamp=timezone.now()
                    )
                
                # Activar portones automáticos
                portones = Dispositivo.objects.filter(tipo='PORTON')
                for porton in portones:
                    AccionIoT.objects.create(
                        incidente=incidente,
                        dispositivo=porton,
                        tipo='EMERGENCIA',
                        accion='ABRIR',
                        detalles={
                            'incidente_id': incidente.id,
                            'motivo': 'Salida de emergencia'
                        },
                        timestamp=timezone.now()
                    )
            
            # Asignar móviles disponibles
            moviles_disponibles = Movil.objects.filter(
                estado='EN_SERVICIO'
            ).order_by('?')[:3]  # Asignar 3 móviles aleatorios
            
            for movil in moviles_disponibles:
                movil.incidente_actual = incidente
                movil.estado = 'EN_CAMINO'
                movil.ultima_actualizacion = timezone.now()
                movil.save()
            
            # Mensaje de éxito
            messages.success(request, f'✅ Incidente #{incidente.id} creado y recursos despachados.')
            
            if toque_sirena:
                messages.warning(request, '⚠️ TOQUE DE SIRENA ACTIVADO - Prioridad Alta')
            
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'❌ Error al crear incidente: {str(e)}')
            return redirect('dashboard')
    
    # Si no es POST, redirigir al dashboard
    return redirect('dashboard')

# Vista para actualizar estado de móvil
@login_required
def actualizar_estado_movil(request, movil_id):
    if request.method == 'POST':
        try:
            movil = Movil.objects.get(id=movil_id)
            nuevo_estado = request.POST.get('estado')
            
            if nuevo_estado in ['EN_SERVICIO', 'FUERA_SERVICIO', 'EN_CAMINO', 'EN_INTERVENCION', 'REG_RESERVA']:
                movil.estado = nuevo_estado
                movil.ultima_actualizacion = timezone.now()
                movil.save()
                
                messages.success(request, f'✅ Estado de Móvil {movil.numero} actualizado a {movil.get_estado_display()}')
            else:
                messages.error(request, '❌ Estado inválido')
                
        except Movil.DoesNotExist:
            messages.error(request, '❌ Móvil no encontrado')
        
        return redirect('dashboard')

# Vista para cerrar incidente
@login_required
def cerrar_incidente(request, incidente_id):
    if request.method == 'POST':
        try:
            incidente = Incidente.objects.get(id=incidente_id)
            incidente.estado = 'CERRADO'
            incidente.fecha_cierre = timezone.now()
            incidente.save()
            
            # Liberar móviles asignados
            moviles_asignados = Movil.objects.filter(incidente_actual=incidente)
            for movil in moviles_asignados:
                movil.incidente_actual = None
                movil.estado = 'EN_SERVICIO'
                movil.save()
            
            messages.success(request, f'✅ Incidente #{incidente.id} cerrado correctamente.')
            
        except Incidente.DoesNotExist:
            messages.error(request, '❌ Incidente no encontrado')
        
        return redirect('dashboard')

# API para obtener sugerencias de direcciones
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def autocomplete_direcciones(request):
    query = request.GET.get('q', '')
    
    # En producción, esto se conectaría a Google Maps API o Nominatim
    sugerencias = [
        "Calle Falsa 123, Buenos Aires",
        "Avenida Siempre Viva 742, Springfield",
        "Calle Principal 456, Ciudad",
        "Avenida Libertador 1234, Capital Federal",
        "Calle San Martín 567, Centro",
        "Avenida Rivadavia 1890, Once",
        "Calle Corrientes 348, Microcentro",
        "Avenida Cabildo 2047, Belgrano",
    ]
    
    # Filtrar por query
    resultados = [s for s in sugerencias if query.lower() in s.lower()][:5]
    
    return Response({'sugerencias': resultados})

# API para obtener coordenadas de una dirección
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_coordenadas(request):
    direccion = request.GET.get('direccion', '')
    
    # En producción, llamar a Google Maps Geocoding API
    coordenadas_ejemplo = {
        'lat': -34.6037,
        'lng': -58.3816,
        'direccion': direccion if direccion else 'Buenos Aires, Argentina'
    }
    
    return Response(coordenadas_ejemplo)

# Vistas de la API REST
class IncidenteViewSet(viewsets.ModelViewSet):
    queryset = Incidente.objects.all().order_by('-fecha_registro')
    serializer_class = IncidenteSerializer

class DispositivoViewSet(viewsets.ModelViewSet):
    queryset = Dispositivo.objects.all().order_by('nombre')
    serializer_class = DispositivoSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def iot_comandos(request):
    device_ip = request.GET.get('device_ip')
    if not device_ip:
        return Response({'detail':'device_ip required'}, status=400)
    pendientes = AccionIoT.objects.filter(dispositivo__direccion_red=device_ip, resultado__isnull=True).order_by('timestamp')[:10]
    serializer = AccionIoTSerializer(pendientes, many=True)
    return Response({'comandos': serializer.data})

@api_view(['POST'])
@permission_classes([AllowAny])
def iot_accion(request):
    data = request.data
    accion_id = data.get('accion_id')
    if not accion_id:
        return Response({'detail':'accion_id required'}, status=400)
    try:
        accion = AccionIoT.objects.get(id=accion_id)
    except AccionIoT.DoesNotExist:
        return Response({'detail':'not found'}, status=404)
    accion.resultado = data.get('resultado', 'OK')
    accion.detalles = data.get('detalles', {})
    accion.save()
    return Response({'status':'ok'})



# Agrega estas funciones en views.py, por ejemplo después de la función dashboard

# Página simple de control de hardware
def control_hardware(request):
    """Página simple para controlar el hardware directamente"""
    return render(request, 'control_hardware.html')

# API para enviar comandos MQTT directos
@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_comando_mqtt(request):
    """API para enviar comandos MQTT (si prefieres no usar MQTT directo en JS)"""
    try:
        data = json.loads(request.body)
        comando = data.get('comando')
        
        # Aquí puedes usar paho-mqtt para enviar el comando
        # Simulación por ahora
        print(f"[MQTT SIMULADO] Enviando comando: {comando}")
        
        # Crear registro en la base de datos
        dispositivo = Dispositivo.objects.filter(tipo='SIRENA').first()
        if dispositivo:
            AccionIoT.objects.create(
                dispositivo=dispositivo,
                tipo='COMANDO_DIRECTO',
                accion=comando,
                detalles={'origen': 'control_hardware'},
                timestamp=timezone.now(),
                resultado='ENVIADO'
            )
        
        return JsonResponse({
            'status': 'success',
            'comando': comando,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

# Otra opción más simple
def control_simple(request):
    """Página de control ultra simple"""
    return render(request, 'control_simple.html')

# API para comandos básicos
@api_view(['GET'])
@permission_classes([AllowAny])
def comando_simple(request):
    """API para comandos simples GET (más fácil de probar)"""
    comando = request.GET.get('c', '')
    
    if comando:
        # Guardar en base de datos
        dispositivo = Dispositivo.objects.filter(tipo='SIRENA').first()
        if not dispositivo:
            dispositivo = Dispositivo.objects.create(
                nombre='ESP32_Sirena',
                tipo='SIRENA',
                direccion_red='192.168.0.8',
                estado='ACTIVO'
            )
        
        AccionIoT.objects.create(
            dispositivo=dispositivo,
            tipo='COMANDO_GET',
            accion=comando,
            detalles={'metodo': 'GET', 'params': dict(request.GET)},
            timestamp=timezone.now(),
            resultado='PENDIENTE'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Comando "{comando}" registrado',
            'comando': comando,
            'timestamp': timezone.now().isoformat()
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'No se especificó comando. Use ?c=SIRENA_ON'
    }, status=400)
