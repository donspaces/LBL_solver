from django.urls import path

from .views import solve_cube

urlpatterns = [
    path('solve/', solve_cube, name='solve_cube'),
]
