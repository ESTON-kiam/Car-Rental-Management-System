from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer_portal/', include('customer_portal.urls')),
    path('car_dealer_portal/', include('car_dealer_portal.urls')),
    path('', include('home.urls')),
]
