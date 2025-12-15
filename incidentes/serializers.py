from rest_framework import serializers
from .models import Dispositivo, Incidente, AccionIoT, Movil, Llamada, TiemposIncidente, LogSistema

class DispositivoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Dispositivo
        fields = '__all__'

class IncidenteSerializer(serializers.ModelSerializer):
    operador_nombre = serializers.CharField(source='operador.get_full_name', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Incidente
        fields = '__all__'

class MovilSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Movil
        fields = '__all__'

class LlamadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Llamada
        fields = '__all__'

class AccionIoTSerializer(serializers.ModelSerializer):
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    incidente_id = serializers.IntegerField(source='incidente.id', read_only=True)
    
    class Meta:
        model = AccionIoT
        fields = '__all__'

class TiemposIncidenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiemposIncidente
        fields = '__all__'

class LogSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSistema
        fields = '__all__'