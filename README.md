# RecetaSmart - Starter Django Project

Este es un esqueleto inicial para el proyecto **bomberos** (Recepción y Despacho).
Incluye:
- Proyecto Django básico
- App `incidentes` con modelos esenciales
- Serializers y Views (Django REST Framework)
- Endpoints API básicos para integrarse con placas IoT
- Instrucciones para correr en desarrollo (SQLite)

## Requisitos
- Python 3.10+ recomendado
- pip

## Instrucciones rápidas
1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Migraciones:
   ```bash
   python manage.py migrate
   ```
4. Crear superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Correr servidor:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

La API base estará en `/api/`.

## Archivos generados
- manage.py
- recetasmart_project/ (settings, urls)
- incidentes/ (models, serializers, views, urls)
- templates/ (plantillas mínimas)

Siguiente paso: te puedo generar el proyecto con Postgres, Dockerfile y configurar autenticación para dispositivos IoT.
