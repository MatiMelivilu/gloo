from django.urls import path
from . import views

urlpatterns = [
    path('procesar/', views.procesar_servicio, name='procesar_servicio'),
]
