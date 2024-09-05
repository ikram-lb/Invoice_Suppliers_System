from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta

# Fournisseur Model
class Fournisseur(models.Model):
    nom_societe = models.CharField(max_length=255)
    nom_personne = models.CharField(max_length=255, blank=True, null=True)
    adresse_facturation = models.CharField(max_length=255, blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    pays_region = models.CharField(max_length=100, blank=True, null=True)
    numeros_telephone = models.TextField(blank=True, null=True)
    emails = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom_societe

# Client Model
class Client(models.Model):
    
    numero_Client = models.IntegerField(unique=True)
    N_ICE_Client = models.IntegerField(unique=True)
    nom_societe = models.CharField(max_length=255)
    name = models.CharField(max_length=132)
    email = models.EmailField()
    phone = models.CharField(max_length=132)
    address = models.CharField(max_length=64)
    city = models.CharField(max_length=32)
    Pays = models.CharField(max_length=32)
    zip_code = models.CharField(max_length=16)
    created_date = models.DateTimeField(auto_now_add=True)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

# Produit Model
class Produit(models.Model):
    nom = models.CharField(max_length=255)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='produits')
    description = models.TextField(blank=True, null=True)
    prixUnitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom


# Commande Model
class Commande(models.Model):
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='commandes')
    numero = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    montant = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    produits = models.ManyToManyField(Produit, through='CommandeProduit')

    def save(self, *args, **kwargs):
     if self.pk:
        self.montant = sum(cp.produit.prixUnitaire * cp.quantite for cp in self.commandeproduits.all())
     super().save(*args, **kwargs)


    def __str__(self):
        return self.numero

# CommandeProduit Model
class CommandeProduit(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='commandeproduits')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.commande.numero} - {self.produit.nom}'


# Facture Model
def get_default_fournisseur():
    return Fournisseur.objects.first() or None

class Facture(models.Model):
    STATUT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]
    fournisseur = models.ForeignKey(Fournisseur, default=get_default_fournisseur, on_delete=models.CASCADE)
    # commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='factures')
    numero = models.CharField(max_length=255, unique=True)
    date = models.DateField(default=timezone.now)
    montant = models.DecimalField(max_digits=20, decimal_places=2)
    fichier = models.FileField(upload_to='factures/', null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATUT_CHOICES, default='unpaid')

    def __str__(self):
        return f'Facture {self.numero} - {self.fournisseur.nom_societe}'
    
    def get_absolute_url(self):
        return reverse('view_facture', kwargs={'pk': self.pk})


# Axians Invoice model 
class Invoice(models.Model):

    customer = models.ForeignKey(Client, on_delete=models.PROTECT)
    
    numero = models.IntegerField(unique=True)
    date_commande = models.DateField()
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    invoice_date_time = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(max_digits=100, decimal_places=2)

    last_updated_date = models.DateTimeField(null=True, blank=True)

    paid  = models.BooleanField(default=False)

    comments = models.TextField(null=True, max_length=1000, blank=True)
    
    vat_rate = Decimal('0.20') # 20% VAT
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
           return f"{self.customer.name}_{self.invoice_date_time}"

    @property
    def get_total(self):
        articles = self.article_set.all()   
        total = sum(article.get_total for article in articles)
        return total    
    @property
    def vat_amount(self):
        return self.total * self.vat_rate

    @property
    def total_with_vat(self):
        return self.total + self.vat_amount
    
    @property
    def due_date(self):
        # Add 2 months to the invoice date
        if self.invoice_date_time:
            return self.invoice_date_time + relativedelta(months=2)
        return None


# Article model 
class Article(models.Model):

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    name = models.CharField(max_length=32)

    quantity = models.IntegerField()

    unit_price = models.DecimalField(max_digits=100, decimal_places=2)

    total = models.DecimalField(max_digits=100, decimal_places=2)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    @property
    def get_total(self):
        total = self.quantity * self.unit_price   
        return total 
        