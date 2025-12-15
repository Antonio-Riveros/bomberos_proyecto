from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Elimina el modelo Operador existente o coméntalo
# class Operador(models.Model):
#     nombre = models.CharField(max_length=120)
#     usuario = models.CharField(max_length=80, unique=True)
#     password_hash = models.CharField(max_length=256)
#     rol = models.CharField(max_length=30)
#     turno = models.CharField(max_length=30, null=True, blank=True)
#     creado_at = models.DateTimeField(auto_now_add=True)
# 
#     def __str__(self):
#         return f"{self.nombre} ({self.usuario})"

class Dispositivo(models.Model):
    TIPO_CHOICES = [
        ('SIRENA', 'Sirena'),
        ('PORTON', 'Portón Automático'),
        ('LUZ', 'Luz de Emergencia'),
        ('RADIO', 'Radio'),
        ('SENSOR', 'Sensor'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    direccion_red = models.GenericIPAddressField(null=True, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, default='ACTIVO')
    ultima_comunicacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

class Incidente(models.Model):
    TIPO_CHOICES = [
        ('FUEGO_ESTRUCTURAL', '🔥 Fuego Estructural'),
        ('RESCATE', '🦺 Rescate'),
        ('ACCIDENTE', '🚑 Accidente'),
        ('FUEGO_FORESTAL', '🌲 Fuego Forestal'),
        ('MATERIALES_PELIGROSOS', '⚠️ Materiales Peligrosos'),
        ('OTRO', '📋 Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('REPORTADO', 'Reportado'),
        ('ASIGNADO', 'Asignado'),
        ('EN_CURSO', 'En Curso'),
        ('CERRADO', 'Cerrado'),
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    direccion = models.CharField(max_length=200)
    detalles = models.TextField()
    prioridad_alta = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='REPORTADO')
    operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='incidentes_atendidos')
    fecha_registro = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    coordenadas_lat = models.FloatField(null=True, blank=True)
    coordenadas_lng = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Incidente #{self.id} - {self.get_tipo_display()} - {self.estado}"
    
    class Meta:
        ordering = ['-fecha_registro']

class Movil(models.Model):
    ESTADO_CHOICES = [
        ('EN_SERVICIO', 'En Servicio'),
        ('FUERA_SERVICIO', 'Fuera de Servicio'),
        ('EN_CAMINO', 'En Camino'),
        ('EN_INTERVENCION', 'En Intervención'),
        ('REG_RESERVA', 'En Reserva'),
    ]
    
    TIPO_CHOICES = [
        ('AUTOBOMBA', 'Autobomba'),
        ('ESCALERA', 'Escalera'),
        ('RESCATE', 'Unidad de Rescate'),
        ('MEDICA', 'Unidad Médica'),
        ('HAZMAT', 'Hazmat'),
        ('COMANDO', 'Vehículo de Comando'),
    ]
    
    numero = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='EN_SERVICIO')
    incidente_actual = models.ForeignKey(Incidente, on_delete=models.SET_NULL, null=True, blank=True, related_name='moviles_asignados')
    ultima_actualizacion = models.DateTimeField(default=timezone.now)
    detalles = models.TextField(blank=True)
    
    def __str__(self):
        return f"Móvil {self.numero} - {self.get_tipo_display()}"
    
    class Meta:
        ordering = ['numero']
        verbose_name_plural = "Móviles"

class Llamada(models.Model):
    numero = models.CharField(max_length=20)
    titular = models.CharField(max_length=100)
    fecha_hora = models.DateTimeField(default=timezone.now)
    incidente_relacionado = models.ForeignKey(Incidente, on_delete=models.SET_NULL, null=True, blank=True)
    duracion = models.DurationField(null=True, blank=True)
    
    def __str__(self):
        return f"Llamada de {self.titular} ({self.numero})"
    
    class Meta:
        ordering = ['-fecha_hora']

class AccionIoT(models.Model):
    incidente = models.ForeignKey(Incidente, null=True, blank=True, on_delete=models.SET_NULL)
    dispositivo = models.ForeignKey(Dispositivo, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.CharField(max_length=40)
    accion = models.CharField(max_length=50)
    detalles = models.JSONField(default=dict, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    resultado = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.dispositivo} - {self.accion} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

class TiemposIncidente(models.Model):
    incidente = models.ForeignKey(Incidente, on_delete=models.CASCADE, related_name='tiempos')
    hora_registro = models.DateTimeField(null=True, blank=True)
    hora_despacho = models.DateTimeField(null=True, blank=True)
    hora_en_ruta = models.DateTimeField(null=True, blank=True)
    hora_llegada = models.DateTimeField(null=True, blank=True)
    hora_cierre = models.DateTimeField(null=True, blank=True)

class LogSistema(models.Model):
    nivel = models.CharField(max_length=20)
    componente = models.CharField(max_length=80)
    mensaje = models.TextField()
    meta = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)