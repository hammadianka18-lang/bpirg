from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import important
from ressources_genetiques import views as res_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', res_views.home, name='home'),

    # 1. Ajoutez ceci pour charger toutes les vues d'authentification (login, logout, password_change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # 2. Vos autres applications
    path('ressources/', include('ressources_genetiques.urls')),
    path('comptes/', include('comptes.urls')),  # Attention au nom 'comptes' vs 'accounts'
]