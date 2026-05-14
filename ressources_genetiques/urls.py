from django.urls import path
from . import views

app_name = 'ressources_genetiques'

urlpatterns = [
    # ACCUEIL / DASHBOARD
    path('', views.home, name='home'),  # Route pour la page d'accueil
    path('catalogue/', views.liste_publique, name='liste_publique'),
    path('dashboard/', views.dashboard_ressources, name='dashboard'),

    # GESTION DES RESSOURCES (CRUD)
    path('saisie/', views.saisie_ressource, name='saisie'),
    path('liste/', views.liste_ressources, name='liste'),
    path('modifier/<int:pk>/', views.modifier_ressource, name='modifier'),
    path('supprimer/<int:pk>/', views.supprimer_ressource, name='supprimer'),

    # IMPORTATION
    path('import/', views.import_ressources, name='import'),

    # PARAMÉTRAGE DES LISTES (Nouvel onglet pour l'Admin)
    path('configuration/', views.configuration_listes, name='configuration'),

    # ROUTES AJAX POUR LES LISTES EN CASCADE (Appelées par le JavaScript)
    path('ajax/load-categories/', views.load_categories, name='ajax_load_categories'),
    path('ajax/load-noms/', views.load_noms_ressources, name='ajax_load_noms'),
    path('ajax/load-especes/', views.load_especes, name='ajax_load_especes'),
]