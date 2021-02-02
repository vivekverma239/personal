from django.urls import path, include
from .views import  *

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"constant", ConstantViewSet)
router.register(r"stocks", StockDataViewSet)
router.register(r"strategy", StrategyViewSet)
router.register(r"search_file", SearchFileViewSet)



urlpatterns = [
    path("", include(router.urls)),
    path('search/', SearchFileMethod.as_view({'get': 'retrieve'})),
    path('search_section/', SearchFileMethod.as_view({'get': 'retrieve_section'})),
    path('highlight/', SearchFileMethod.as_view({'get': 'highlight'})),
]