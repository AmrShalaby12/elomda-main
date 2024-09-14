from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf import settings
from django.conf.urls.static import static
from .views import scan_qr
from . import views  

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup_view, name="signup"),
    path('', views.scan_qr, name='scan_qr'),
    path('attendance/', views.attendance_view, name='attendance'),  # المسار الجديد للحضور
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
