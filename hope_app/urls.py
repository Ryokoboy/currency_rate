from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name="Index"),
    path('data', get_data, name='data'),
]