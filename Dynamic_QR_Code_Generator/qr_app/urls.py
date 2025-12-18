from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_qr/', views.create_qr, name='create_qr'),
    path('r/<str:short_id>/', views.redirect_qr, name='redirect_qr'),
    path('qr_stats/<str:short_id>/', views.qr_stats, name='qr_stats'),
    path('update_qr/<str:short_id>/', views.update_qr, name='update_qr'), # http://127.0.0.1:8000/update_qr/<short_id>/


    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
