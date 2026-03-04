from django.urls import include, path

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('api/', include('cube_solver_api.urls')),
]
