from django.db import models
from django.conf import settings


# 1. NATURE GÉNÉTIQUE (Ex: Accession, Lignée)
class NatureGenetique(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Nature Génétique"
        ordering = ['nom']

    def __str__(self):
        return self.nom


# 2. TYPE DE RESSOURCE (Ex: Végétale, Animale, Microbienne)
class TypeRessource(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Type de Ressource"
        ordering = ['nom']

    def __str__(self):
        return self.nom


# 3. CATÉGORIE (Ex: Céréales, Légumineuses - Liée au Type)
class Categorie(models.Model):
    type_ressource = models.ForeignKey(TypeRessource, on_delete=models.CASCADE, related_name='categories')
    nom = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Catégorie"
        unique_together = ('type_ressource', 'nom')  # Évite les doublons dans un même type
        ordering = ['nom']

    def __str__(self):
        return self.nom


# 4. RESSOURCE GÉNÉTIQUE NOM (Ex: RIZ, MAIS - Liée à la Catégorie)
class NomRessource(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='ressources_noms')
    nom = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Nom de la Ressource"
        unique_together = ('categorie', 'nom')
        ordering = ['nom']

    def __str__(self):
        return self.nom


# 5. ESPÈCE (Ex: Oryza sativa - Liée au Nom de la Ressource)
class Espece(models.Model):
    nom_ressource = models.ForeignKey(NomRessource, on_delete=models.CASCADE, related_name='especes')
    nom = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Espèce"
        unique_together = ('nom_ressource', 'nom')
        ordering = ['nom']

    def __str__(self):
        return self.nom


# 6. MODÈLE PRINCIPAL (RessourceGenetique)
class RessourceGenetique(models.Model):
    # Les listes en cascade
    type_ressource = models.ForeignKey(TypeRessource, on_delete=models.PROTECT, verbose_name="Type de ressource")
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, verbose_name="Catégorie")
    nom_ressource = models.ForeignKey(NomRessource, on_delete=models.PROTECT, verbose_name="Ressource génétique")
    espece = models.ForeignKey(Espece, on_delete=models.PROTECT, verbose_name="Espèce")

    # Champ libre
    denomination = models.CharField(max_length=150, verbose_name="Dénomination")

    # Référence
    nature_genetique = models.ForeignKey(NatureGenetique, on_delete=models.PROTECT, verbose_name="Nature génétique")

    # Traçabilité
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Ressource Génétique"
        verbose_name_plural = "Ressources Génétiques"
        ordering = ['-date_enregistrement']

    def __str__(self):
        # On ne renvoie que le nom de la dénomination pour la base
        return self.denomination