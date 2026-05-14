from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import (
    RessourceGenetique, NatureGenetique, TypeRessource,
    Categorie, NomRessource, Espece
)

# Configuration simple pour les tables de base
@admin.register(NatureGenetique)
class NatureGenetiqueAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(TypeRessource)
class TypeRessourceAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

# Configuration pour les tables avec relations (ForeignKey)
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_ressource')
    list_filter = ('type_ressource',)
    search_fields = ('nom',)

@admin.register(NomRessource)
class NomRessourceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie')
    list_filter = ('categorie__type_ressource', 'categorie')
    search_fields = ('nom',)

@admin.register(Espece)
class EspeceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nom_ressource')
    search_fields = ('nom',)

# =====================================================
# CONFIGURATION RESSOURCE GÉNÉTIQUE
# =====================================================
@admin.register(RessourceGenetique)
class RessourceGenetiqueAdmin(admin.ModelAdmin):
    # Colonnes affichées (On utilise les noms des modèles liés)
    list_display = (
        'denomination',
        'nom_ressource',
        'espece',
        'nature_genetique',
        'type_ressource',
        'date_enregistrement'
    )

    # Filtres latéraux optimisés pour les relations
    list_filter = (
        'type_ressource',
        'nature_genetique',
        'categorie',
    )

    # Recherche (On pointe vers le champ 'nom' des modèles liés avec __nom)
    search_fields = (
        'denomination',
        'nom_ressource__nom',
        'espece__nom',
        'categorie__nom'
    )

    # Action personnalisée pour exporter en CSV
    actions = ["exporter_csv"]

    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="patrimoine_genetique.csv"'
        response.write('\ufeff'.encode('utf8')) # Gérer les accents pour Excel

        writer = csv.writer(response)
        writer.writerow([
            'Dénomination',
            'Ressource',
            'Espèce',
            'Catégorie',
            'Nature',
            'Type'
        ])

        # .select_related évite de faire des centaines de requêtes SQL
        for obj in queryset.select_related('nom_ressource', 'espece', 'categorie', 'nature_genetique', 'type_ressource'):
            writer.writerow([
                obj.denomination,
                obj.nom_ressource.nom,
                obj.espece.nom,
                obj.categorie.nom,
                obj.nature_genetique.nom,
                obj.type_ressource.nom,
            ])

        return response

    exporter_csv.short_description = "📥 Exporter le patrimoine sélectionné (CSV)"