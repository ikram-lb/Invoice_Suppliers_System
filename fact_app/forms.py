from django import forms
from .models import CommandeProduit, Facture, Fournisseur, Produit, Commande, Client
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = [
            'nom_societe',
            'nom_personne',
            'adresse_facturation',
            'ville',
            'pays_region',
            'numeros_telephone',
            'emails',
            'notes'
        ]
        widgets = {
            'numeros_telephone': forms.TextInput(attrs={'placeholder': 'Enter phone numbers separated by commas'}),
            'emails': forms.TextInput(attrs={'placeholder': 'Enter emails separated by commas'}),
        }

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'description', 'prixUnitaire']

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['fournisseur', 'numero', 'date']  # Don't include montant here
        
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if self.instance.pk:
            if Commande.objects.filter(numero=numero).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This numero is already assigned to another Commande.')
        else:
            if Commande.objects.filter(numero=numero).exists():
                raise forms.ValidationError('This numero is already assigned to another Commande.')
        return numero    

    def clean(self):
        cleaned_data = super().clean()
        produits = self.data.getlist('products[]')
        quantites = self.data.getlist('quantities[]')

        if produits and quantites:
            if len(produits) != len(quantites):
                raise forms.ValidationError("The number of quantities must match the number of selected products.")

            for quantity in quantites:
                if not quantity.isdigit() or int(quantity) <= 0:
                    raise forms.ValidationError("Quantities must be valid positive integers.")

            # Calculate montant
            montant = 0
            for produit_id, quantity in zip(produits, quantites):
                try:
                    produit = Produit.objects.get(pk=produit_id)
                    montant += produit.prixUnitaire * int(quantity)
                except Produit.DoesNotExist:
                    raise forms.ValidationError("Selected product does not exist.")
            
            # Store montant in cleaned_data
            cleaned_data['montant'] = montant

        return cleaned_data

    def save(self, commit=True):
        commande = super().save(commit=False)
        # Set montant before saving
        produits = self.data.getlist('products[]')
        quantites = list(map(int, self.data.getlist('quantities[]')))
        
        # Calculate montant
        montant = 0
        for produit_id, quantite in zip(produits, quantites):
            try:
                produit = Produit.objects.get(pk=produit_id)
                montant += produit.prixUnitaire * quantite
            except Produit.DoesNotExist:
                raise forms.ValidationError("Selected product does not exist.")
        
        commande.montant = montant

        if commit:
            commande.save()
            # Clear existing CommandeProduit relationships
            CommandeProduit.objects.filter(commande=commande).delete()
            # Create new CommandeProduit relationships
            for produit_id, quantite in zip(produits, quantites):
                produit = Produit.objects.get(pk=produit_id)
                CommandeProduit.objects.create(
                    commande=commande,
                    produit=produit,
                    quantite=quantite
                )
        
        return commande

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['fournisseur', 'numero', 'date', 'montant', 'fichier', 'state']
        widgets = {
            'state': forms.Select(choices=[
                ('unpaid', 'Unpaid'),
                ('paid', 'Paid')
            ]),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom_societe','name', 'email', 'phone', 'address','city','Pays','zip_code', 'save_by']
        widgets = {
          
        }

class SuperUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = True
        user.is_staff = True
        if commit:
            user.save()
        return user

