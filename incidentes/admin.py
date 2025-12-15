from django.contrib import admin
from .models import Dispositivo, Incidente, TiemposIncidente, AccionIoT, LogSistema, Movil, Llamada

# No registramos Operador ya que usamos User de Django
# admin.site.register(Operador)

admin.site.register(Dispositivo)
admin.site.register(Incidente)
admin.site.register(TiemposIncidente)
admin.site.register(AccionIoT)
admin.site.register(LogSistema)
admin.site.register(Movil)
admin.site.register(Llamada)