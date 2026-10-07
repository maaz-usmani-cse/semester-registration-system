from django.contrib import admin
from django.urls import path, include
from django.conf import settings                  # <-- YE WAPAS CHECK KARO
from django.conf.urls.static import static        # <-- YE WAPAS CHECK KARO
from dashboard.views import create_admin_account  # import karein
urlpatterns = [
    path('admin/', admin.site.urls),
    path('make-my-admin/', create_admin_account),
    path('dashboard/',include('dashboard.urls')),
    path('', include('app.urls')), # Aapke app ka jo bhi naam ho ('app' ya 'registration')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

