from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .forms import RessourceGenetiqueForm
from .models import (
    RessourceGenetique, NatureGenetique, TypeRessource,
    Categorie, NomRessource, Espece
)


# =====================================================
# ACCUEIL ET LISTE
# =====================================================

def home(request):
    """Page d'accueil publique \ Vitrine """
    if request.user.is_authenticated:
        return redirect('ressources_genetiques:dashboard')

    # Calcul des KPI pour les 5 types de ressources
    kpis = {
        'vegetale': RessourceGenetique.objects.filter(type_ressource__nom__icontains="Végétale").count(),
        'animale': RessourceGenetique.objects.filter(type_ressource__nom__icontains="Animale").count(),
        'forestiere': RessourceGenetique.objects.filter(type_ressource__nom__icontains="Forestière").count(),
        'fruitiere': RessourceGenetique.objects.filter(type_ressource__nom__icontains="Fruitière").count(),
        'halieutique': RessourceGenetique.objects.filter(type_ressource__nom__icontains="Halieutique").count(),
    }

    return render(request, 'ressources_genetiques/home.html', {'kpis': kpis})


def liste_publique(request):
    """Vue pour le public avec support de recherche dynamique (AJAX)"""
    type_nom = request.GET.get('type')
    query = request.GET.get('q', '').strip()

    ressources_list = RessourceGenetique.objects.all().select_related('type_ressource', 'espece', 'categorie',
                                                                      'nom_ressource', 'nature_genetique')

    # Filtrage par type (clic depuis l'accueil)
    if type_nom:
        ressources_list = ressources_list.filter(type_ressource__nom__icontains=type_nom)

    # Filtrage par recherche dynamique
    if query:
        ressources_list = ressources_list.filter(
            denomination__icontains=query
        ) | ressources_list.filter(
            nom_ressource__nom__icontains=query
        ) | ressources_list.filter(
            espece__nom__icontains=query
        )

    # Si c'est une requête AJAX (JavaScript)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for r in ressources_list[:50]:  # Limiter à 50 pour la performance en dynamique
            data.append({
                'categorie': str(r.categorie),
                'ressource': str(r.nom_ressource),
                'espece': str(r.espece),
                'denomination': r.denomination,
                'nature': r.nature_genetique.nom if r.nature_genetique else "N/A",
            })
        return JsonResponse({'results': data})

    # Chargement initial classique
    paginator = Paginator(ressources_list, 15)
    page_number = request.GET.get('page')
    ressources = paginator.get_page(page_number)

    return render(request, 'ressources_genetiques/liste_publique.html', {
        'ressources': ressources,
        'type_nom': type_nom
    })

## Partie liste dashbord

@login_required
def liste_ressources(request):
    """Vue pour afficher la base de données complète avec pagination."""
    ressources_list = RessourceGenetique.objects.all().select_related(
        'type_ressource', 'categorie', 'nom_ressource', 'espece', 'nature_genetique', 'utilisateur'
    )

    query = request.GET.get('q')
    if query:
        ressources_list = ressources_list.filter(
            denomination__icontains=query
        ) | ressources_list.filter(
            espece__nom__icontains=query
        )

    paginator = Paginator(ressources_list, 10)
    page_number = request.GET.get('page')
    ressources = paginator.get_page(page_number)

    return render(request, 'ressources_genetiques/liste.html', {'ressources': ressources})


# =====================================================
# SAISIE ET MODIFICATION
# =====================================================

@login_required
def saisie_ressource(request):
    if request.method == 'POST':
        form = RessourceGenetiqueForm(request.POST)
        if form.is_valid():
            # On récupère les données sans les enregistrer immédiatement
            cleaned_data = form.cleaned_data

            # Vérification de l'existence (même logique que l'import)
            # On cherche une ressource avec la même espèce et la même dénomination
            exist_query = RessourceGenetique.objects.filter(
                espece=cleaned_data['espece'],
                denomination=cleaned_data['denomination']
            )

            if exist_query.exists():
                # On récupère l'existant pour personnaliser le message
                obj = exist_query.first()
                messages.warning(request,
                                 f"⚠️ Cette ressource ({obj.denomination} - {obj.espece}) existe déjà dans la base BPIRG.")
                # On reste sur la page de saisie avec les données pour correction
                return render(request, 'ressources_genetiques/saisie.html', {'form': form})

            # Si elle n'existe pas, on procède à l'enregistrement
            ressource = form.save(commit=False)
            ressource.utilisateur = request.user
            ressource.save()
            messages.success(request, "✅ La ressource génétique a été enregistrée avec succès.")
            return redirect('ressources_genetiques:dashboard')
    else:
        form = RessourceGenetiqueForm()
    return render(request, 'ressources_genetiques/saisie.html', {'form': form})

@login_required
def modifier_ressource(request, pk):
    ressource = get_object_or_404(RessourceGenetique, pk=pk)
    if request.method == 'POST':
        form = RessourceGenetiqueForm(request.POST, instance=ressource)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ La ressource '{ressource.denomination}' a été mise à jour.")
            return redirect('ressources_genetiques:liste')
    else:
        form = RessourceGenetiqueForm(instance=ressource)

    return render(request, 'ressources_genetiques/modifier.html', {
        'form': form,
        'ressource': ressource
    })


@login_required
def supprimer_ressource(request, pk):
    ressource = get_object_or_404(RessourceGenetique, pk=pk)
    if request.method == 'POST':
        nom = ressource.denomination
        ressource.delete()
        messages.warning(request, f"🗑️ La ressource '{nom}' a été supprimée.")
        return redirect('ressources_genetiques:liste')
    return render(request, 'ressources_genetiques/confirmer_suppression.html', {'ressource': ressource})


# =====================================================
# DASHBOARD
# =====================================================

import json
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import RessourceGenetique, Categorie, Espece, NatureGenetique, TypeRessource

@login_required
def dashboard_ressources(request):
    # 1. Récupération des filtres
    cat_id = request.GET.get('categorie')
    esp_id = request.GET.get('espece')
    nat_id = request.GET.get('nature')
    type_id = request.GET.get('type_ressource') # Nouveau filtre

    # Queryset de base
    ressources = RessourceGenetique.objects.all()

    # 2. Application des filtres
    if cat_id: ressources = ressources.filter(categorie_id=cat_id)
    if esp_id: ressources = ressources.filter(espece_id=esp_id)
    if nat_id: ressources = ressources.filter(nature_genetique_id=nat_id)
    if type_id: ressources = ressources.filter(type_ressource_id=type_id) # Nouveau filtre

    # 3. Calcul des KPI
    total_ressources = ressources.count()
    nb_especes_filtrees = ressources.values('espece').distinct().count()
    nb_categories_filtrees = ressources.values('categorie').distinct().count()

    top_nature_query = ressources.values('nature_genetique__nom').annotate(total=Count('id')).order_by('-total').first()
    top_nature = top_nature_query['nature_genetique__nom'] if top_nature_query else "N/A"

    # 4. Statistiques pour les graphiques
    stats_cat = ressources.values('categorie__nom').annotate(total=Count('id')).order_by('-total')[:5]
    stats_nat = ressources.values('nature_genetique__nom').annotate(total=Count('id')).order_by('-total')

    context = {
        'total_ressources': total_ressources,
        'nb_especes': nb_especes_filtrees,
        'nb_categories': nb_categories_filtrees,
        'top_nature': top_nature,

        # Listes pour les menus déroulants
        'categories': Categorie.objects.all().order_by('nom'),
        'especes': Espece.objects.all().order_by('nom'),
        'natures': NatureGenetique.objects.all().order_by('nom'),
        'types_ressources': TypeRessource.objects.all().order_by('nom'), # Nouveau

        'labels_cat': json.dumps([s['categorie__nom'] for s in stats_cat]),
        'data_cat': json.dumps([s['total'] for s in stats_cat]),
        'labels_nat': json.dumps([s['nature_genetique__nom'] for s in stats_nat]),
        'data_nat': json.dumps([s['total'] for s in stats_nat]),

        # Conservation de l'état des filtres
        'selected_cat': cat_id,
        'selected_esp': esp_id,
        'selected_nat': nat_id,
        'selected_type': type_id, # Nouveau
    }
    return render(request, 'ressources_genetiques/dashboard.html', context)
# =====================================================
# AJAX : CASCADE
# =====================================================

@login_required
def load_categories(request):
    type_id = request.GET.get('type_id')
    categories = Categorie.objects.filter(type_ressource_id=type_id).order_by('nom')
    return JsonResponse(list(categories.values('id', 'nom')), safe=False)


@login_required
def load_noms_ressources(request):
    categorie_id = request.GET.get('categorie_id')
    noms = NomRessource.objects.filter(categorie_id=categorie_id).order_by('nom')
    return JsonResponse(list(noms.values('id', 'nom')), safe=False)


@login_required
def load_especes(request):
    nom_ressource_id = request.GET.get('nom_ressource_id')
    especes = Espece.objects.filter(nom_ressource_id=nom_ressource_id).order_by('nom')
    return JsonResponse(list(especes.values('id', 'nom')), safe=False)


# =====================================================
# CONFIGURATION ET IMPORT
# =====================================================

@login_required
def configuration_listes(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # 'ajouter', 'modifier' ou 'supprimer'
        type_action = request.POST.get('type_action')
        item_id = request.POST.get('item_id')
        nom = request.POST.get('nom')

        # Dictionnaire pour mapper le type_action au Modèle Django
        model_map = {
            'nature': NatureGenetique,
            'type': TypeRessource,
            'categorie': Categorie,
            'nom_ressource': NomRessource,
            'espece': Espece,
        }

        model = model_map.get(type_action)

        if action == 'ajouter':
            if type_action in ['nature', 'type']:
                model.objects.create(nom=nom)
            else:
                parent_id = request.POST.get('parent_id')
                parent_field = 'type_ressource_id' if type_action == 'categorie' else \
                    'categorie_id' if type_action == 'nom_ressource' else 'nom_ressource_id'
                model.objects.create(nom=nom, **{parent_field: parent_id})
            messages.success(request, f"✅ '{nom}' ajouté.")

        elif action == 'modifier':
            obj = get_object_or_404(model, id=item_id)
            ancien_nom = obj.nom
            obj.nom = nom
            obj.save()
            messages.info(request, f"✏️ '{ancien_nom}' a été renommé en '{nom}'.")

        elif action == 'supprimer':
            obj = get_object_or_404(model, id=item_id)
            try:
                nom_supprime = obj.nom
                obj.delete()
                messages.warning(request, f"🗑️ '{nom_supprime}' a été supprimé.")
            except Exception:
                messages.error(request,
                               "❌ Impossible de supprimer cet élément car il est lié à des ressources existantes.")

        return redirect('ressources_genetiques:configuration')

    context = {
        'natures': NatureGenetique.objects.all().order_by('nom'),
        'types': TypeRessource.objects.all().order_by('nom'),
        'categories': Categorie.objects.select_related('type_ressource').all().order_by('nom'),
        'noms_ressources': NomRessource.objects.select_related('categorie').all().order_by('nom'),
        'especes': Espece.objects.select_related('nom_ressource').all().order_by('nom'),
    }
    return render(request, 'ressources_genetiques/configuration.html', context)
    # Données pour l'affichage
    context = {
        'natures': NatureGenetique.objects.all().order_by('nom'),
        'types': TypeRessource.objects.all().order_by('nom'),
        'categories': Categorie.objects.select_related('type_ressource').all().order_by('nom'),
        'noms_ressources': NomRessource.objects.select_related('categorie').all().order_by('nom'),
        'especes': Espece.objects.select_related('nom_ressource').all().order_by('nom'),
    }
    return render(request, 'ressources_genetiques/configuration.html', context)


#################################
# Importation
################################

import pandas as pd
from django.db import transaction


@login_required
def import_ressources(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)

            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for _, row in df.iterrows():
                    # 1. Extraction et nettoyage
                    type_nom = str(row['TYPE DE RESSOURCE']).strip()
                    nature_nom = str(row['NATURE GÉNÉTIQUE']).strip()
                    cat_nom = str(row['CATEGORIE']).strip()
                    res_nom = str(row['RESSOURCE GÉNÉTIQUE']).strip()
                    esp_nom = str(row['ESPÈCE']).strip() if pd.notna(row['ESPÈCE']) else "ND"
                    denom = str(row['DÉNOMINATION']).strip()

                    # 2. Récupération/Création des dépendances
                    type_obj, _ = TypeRessource.objects.get_or_create(nom=type_nom)
                    nature_obj, _ = NatureGenetique.objects.get_or_create(nom=nature_nom)
                    cat_obj, _ = Categorie.objects.get_or_create(nom=cat_nom, type_ressource=type_obj)
                    nom_res_obj, _ = NomRessource.objects.get_or_create(nom=res_nom, categorie=cat_obj)
                    espece_obj, _ = Espece.objects.get_or_create(nom=esp_nom, nom_ressource=nom_res_obj)

                    # 3. GESTION DES DOUBLONS
                    # On cherche si une ressource existe déjà avec ces critères précis
                    ressource, created = RessourceGenetique.objects.get_or_create(
                        type_ressource=type_obj,
                        categorie=cat_obj,
                        nom_ressource=nom_res_obj,
                        espece=espece_obj,
                        denomination=denom,
                        defaults={
                            'nature_genetique': nature_obj,
                            'utilisateur': request.user
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        #  Mettre à jour la nature si elle a changé dans le fichier
                        ressource.nature_genetique = nature_obj
                        ressource.save()
                        updated_count += 1

            messages.success(request,
                             f"✅ Importation terminée : {created_count} nouvelles ressources, {updated_count} mises à jour.")
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de l'importation : {str(e)}")

        return redirect('ressources_genetiques:dashboard')

    return render(request, 'ressources_genetiques/import.html')