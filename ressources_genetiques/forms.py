from django import forms
from .models import RessourceGenetique, TypeRessource, Categorie, NomRessource, Espece, NatureGenetique


class RessourceGenetiqueForm(forms.ModelForm):
    class Meta:
        model = RessourceGenetique
        # On exclut les champs automatiques
        exclude = ['date_enregistrement', 'utilisateur']

        widgets = {
            'type_ressource': forms.Select(attrs={'class': 'form-select', 'id': 'id_type_ressource'}),
            'categorie': forms.Select(attrs={'class': 'form-select', 'id': 'id_categorie'}),
            'nom_ressource': forms.Select(attrs={'class': 'form-select', 'id': 'id_nom_ressource'}),
            'espece': forms.Select(attrs={'class': 'form-select', 'id': 'id_espece'}),
            'nature_genetique': forms.Select(attrs={'class': 'form-select'}),
            'denomination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: DJIBABOUYA'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personnalisation des labels
        self.fields['type_ressource'].label = "Type de ressource"
        self.fields['categorie'].label = "Catégorie"
        self.fields['nom_ressource'].label = "Ressource génétique (Nom)"
        self.fields['espece'].label = "Espèce"
        self.fields['nature_genetique'].label = "Nature génétique"
        self.fields['denomination'].label = "Dénomination"

        # Logique pour les listes en cascade :
        # Si on crée une nouvelle ressource (pas d'instance/données POST),
        # on vide les querysets des listes dépendantes pour forcer l'ordre de sélection.

        if 'type_ressource' not in self.data:
            self.fields['categorie'].queryset = Categorie.objects.none()
            self.fields['nom_ressource'].queryset = NomRessource.objects.none()
            self.fields['espece'].queryset = Espece.objects.none()
        elif self.data.get('type_ressource'):
            try:
                type_id = int(self.data.get('type_ressource'))
                self.fields['categorie'].queryset = Categorie.objects.filter(type_ressource_id=type_id)
            except (ValueError, TypeError):
                pass

        # On répète la logique pour les niveaux suivants si nécessaire (lors d'une erreur de validation)
        if self.data.get('categorie'):
            try:
                cat_id = int(self.data.get('categorie'))
                self.fields['nom_ressource'].queryset = NomRessource.objects.filter(categorie_id=cat_id)
            except (ValueError, TypeError):
                pass