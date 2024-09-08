from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf import settings
from django.conf.urls.static import static
from .views import process_payment
from .views import scan_qr
from . import views  

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup_view, name="signup"),
    path("cart", views.cart_view, name="cart"),
    path("order", views.order_view, name="order"),
    path("topping/<int:cart_id>/", views.topping_view, name="topping"),
    path("removefromcart/<int:cart_id>/", views.removefromcart_view, name="removefromcart"),
    path('cart_count/', views.cart_count, name='cart_count'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='cart_add'),
    path('submit_feedback', views.submit_feedback, name='submit_feedback'),  # المسار الجديدئ
    path('cart/', views.cart_view, name='cart_view'),
    path('process_payment/', process_payment, name='process_payment'),
    path('', views.scan_qr, name='scan_qr'),
    path('attendance/', views.attendance_view, name='attendance'),  # المسار الجديد للحضور

    

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
