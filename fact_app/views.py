import uuid
from django.shortcuts import render
from django.views import View
from .models import * 
from django.contrib import messages
from django.http import HttpResponse
import pdfkit
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import get_template
from django.template.loader import get_template
from django.db import transaction
from django.utils.translation import gettext as _
import pdfkit
import datetime
from django.db import transaction
from .utils import pagination, get_invoice
from .decorators import *
from .models import Article, Client, Facture, Invoice, Produit
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import pagination, get_invoice
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import reverse_lazy
import openpyxl
from .models import Commande, CommandeProduit, Fournisseur, Produit, Facture
from .forms import FournisseurForm, ProduitForm, FactureForm, CommandeForm, SuperUserCreationForm
from django.core.paginator import Paginator
from django.contrib import messages
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from django.views.decorators.http import require_POST
logger = logging.getLogger(__name__)

# Axians invoice system Client Article Invoice models 
   
# Add Client to asign for every Client a new Invoice

class AddCustomerView(LoginRequiredMixin, View):
    """ Add new customer """    
    template_name = 'Invoice/add_customer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
      
    def post(self, request, *args, **kwargs):
        max_numeroo = Client.objects.aggregate(max_numeroo=models.Max('numero_Client'))['max_numeroo']
        numero_Client = max_numeroo + 6789 if max_numeroo is not None else 1
        max_num = Client.objects.aggregate(max_num=models.Max('N_ICE_Client'))['max_num']
        N_ICE_Client = max_num + 6789 if max_num is not None else 1
        data = {
            'name': request.POST.get('name'),
            'nom_societe': request.POST.get('nom_societe'),
            'Pays': request.POST.get('Pays'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip'),
            'save_by': request.user,
            'numero_Client': numero_Client,
            'N_ICE_Client' : N_ICE_Client,
        }
        try:
            Client.objects.create(**data)
            messages.success(request, "Customer registered successfully.")
        except Exception as e:
            messages.error(request, f"Sorry, our system is detecting the following issues {e}.")
        return redirect('add_customer')  # Redirect to avoid form resubmission
  
# Add New Invoice based on the client and the article designed in this Invoice
class AddInvoiceView(LoginRequiredMixin, View):
    """ add a new invoice view """
    template_name = 'Invoice/add_invoice.html'

    def get(self, request, *args, **kwargs):
        customers = Client.objects.all()
        context = {
            'customers': customers
        }
        return render(request, self.template_name, context)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        
        items = []

        try: 
            customer = request.POST.get('customer')
            articles = request.POST.getlist('article')
            date_commande = request.POST.get('date_commande')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total_a = request.POST.getlist('total-a')
            total = request.POST.get('total')
            comment = request.POST.get('comment')

            # Generate unique numero
            max_numero = Invoice.objects.aggregate(max_numero=models.Max('numero'))['max_numero']
            numero = max_numero + 12346 if max_numero is not None else 1

            invoice_object = {
                'customer_id': customer,
                'save_by': request.user,
                'total': total,
                'date_commande': date_commande,
                # 'invoice_type': type,
                'comments': comment,
                'numero': numero
            }

            invoice = Invoice.objects.create(**invoice_object)

            for index, article in enumerate(articles):
                data = Article(
                    invoice_id=invoice.id,
                    name=article,
                    quantity=qties[index],
                    unit_price=units[index],
                    total=total_a[index],
                )
                items.append(data)

            created = Article.objects.bulk_create(items)   

            if created:
                messages.success(request, "Data saved successfully.") 
            else:
                messages.error(request, "Sorry, please try again the sent data is corrupt.")    

        except Exception as e:
            messages.error(request, f"Sorry the following error has occurred: {e}.")   

        customers = Client.objects.all()
        context = {
            'customers': customers
        }
        return render(request, self.template_name, context)
    

# Main view
class HomeView(LoginRequiredSuperuserMixim, View):
    """ Main view """

    templates_name = 'Invoice/index.html'

    invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')

    context = {
        'invoices': invoices
    }

    def get(self, request, *args, **kwags):

        items = pagination(request, self.invoices)

        self.context['invoices'] = items

        return render(request, self.templates_name, self.context)


    def post(self, request, *args, **kwagrs):

        # modify an invoice

        if request.POST.get('id_modified'):

            paid = request.POST.get('modified')

            try: 

                obj = Invoice.objects.get(id=request.POST.get('id_modified'))

                if paid == 'True':

                    obj.paid = True

                else:

                    obj.paid = False 

                obj.save() 

                messages.success(request,  _("Change made successfully.")) 

            except Exception as e:   

                messages.error(request, f"Sorry, the following error has occured {e}.")      

        # deleting an invoice    

        if request.POST.get('id_supprimer'):

            try:

                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))

                obj.delete()

                messages.success(request, _("The deletion was successful."))   

            except Exception as e:

                messages.error(request, f"Sorry, the following error has occured {e}.")      

        items = pagination(request, self.invoices)

        self.context['invoices'] = items

        return render(request, self.templates_name, self.context)    


# Invoice Visualization View
class InvoiceVisualizationView(LoginRequiredMixin, View):
    """ View invoice details """
    template_name = 'Invoice/invoice.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        context = get_invoice(pk)
        return render(request, self.template_name, context)

# Generate the invoice in pdf format
# Need to inject the biblio for generating the pdf
@login_required 
@superuser_required
def get_invoice_pdf(request, *args, **kwargs):
    """ generate pdf file from html file """

    pk = kwargs.get('pk')

    context = get_invoice(pk)

    context['date'] = datetime.datetime.today()

    # get html file
    template = get_template('Invoice/invoice-pdf.html')

    # render html with context variables

    html = template.render(context)

    # options of pdf format 

    options = {
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        "enable-local-file-access": "",
         'no-outline': None,
        'disable-javascript': False,  # Enable if using JS
        'enable-local-file-access': True, 
    }

    # generate pdf 

    pdf = pdfkit.from_string(html, False, options)

    response = HttpResponse(pdf, content_type='application/pdf')

    response['Content-Disposition'] = "attachement"

def index(request):
    fournisseurs = Fournisseur.objects.all().order_by('nom_societe')
    paginator = Paginator(fournisseurs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'polls/index.html', {'fournisseurs': fournisseurs, 'page_obj': page_obj})
@login_required
def add_fournisseur(request):
    if request.method == 'POST':
        fournisseur_form = FournisseurForm(request.POST)
        if fournisseur_form.is_valid():
            fournisseur_form.save()
            messages.success(request, 'Supplier added successfully')
            return redirect('polls')
    else:
        fournisseur_form = FournisseurForm()
    return render(request, 'polls/add_fournisseur.html', {'fournisseur_form': fournisseur_form})
@login_required
def edit_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    if request.method == 'POST':
        fournisseur_form = FournisseurForm(request.POST, instance=fournisseur)
        if fournisseur_form.is_valid():
            fournisseur_form.save()
            messages.success(request, 'Supplier updated successfully')
            return redirect('polls')
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        fournisseur_form = FournisseurForm(instance=fournisseur)

    context = {
        'fournisseur_form': fournisseur_form,
        'fournisseur': fournisseur
    }
    return render(request, 'polls/edit_fournisseur.html', context)
@login_required
def delete_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    fournisseur.delete()
    messages.success(request, 'Supplier removed')
    return redirect('polls')
   
@login_required
def fournisseur_category_summary(request):
    six_months_ago = datetime.date.today() - datetime.timedelta(days=180)
    fournisseurs = Fournisseur.objects.all()
    finalrep = {}

    def get_category(fournisseur):
        return fournisseur.category

    category_list = list(set(map(get_category, fournisseurs)))

    def get_fournisseur_category_amount(category):
        return fournisseurs.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0

    for category in category_list:
        finalrep[category] = get_fournisseur_category_amount(category)

    return JsonResponse({'fournisseur_category_data': finalrep}, safe=False)
@login_required
def fournisseur_detail(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    produits = fournisseur.produits.all()
    return render(request, 'polls/fournisseur_detail.html', {'fournisseur': fournisseur, 'produits': produits})
@login_required
def add_produit_fournisseurs(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.fournisseur = fournisseur
            produit.save()
            return redirect('fournisseur_detail', pk=fournisseur.id)
    else:
        form = ProduitForm()
    return render(request, 'polls/add_produit.html', {'form': form, 'fournisseur': fournisseur})


@login_required
def Products(request):
    produits = Produit.objects.all()
    paginator = Paginator(produits, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'produits': produits,
        'page_obj': page_obj,
    }
    return render(request, 'Products/index.html', context)
@login_required
def add_produit(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        description = request.POST['description']
        prixUnitaire = request.POST['prixUnitaire']
        fournisseur_id = request.POST['fournisseur']

        if not nom or not prixUnitaire or not fournisseur_id:
            messages.error(request, 'All fields are required')
        else:
            fournisseur = get_object_or_404(Fournisseur, pk=fournisseur_id)
            Produit.objects.create(nom=nom, description=description, prixUnitaire=prixUnitaire, fournisseur=fournisseur)
            messages.success(request, 'Produit saved successfully')
            return redirect('Products')
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'Products/add_produit.html', {'fournisseurs': fournisseurs, 'values': request.POST})
@login_required
def edit_produit(request, id):
    produit = get_object_or_404(Produit, pk=id)
    if request.method == 'POST':
        nom = request.POST['nom']
        description = request.POST['description']
        prixUnitaire = request.POST['prixUnitaire']
        fournisseur_id = request.POST['fournisseur']

        if not nom or not prixUnitaire or not fournisseur_id:
            messages.error(request, 'All fields are required')
        else:
            fournisseur = get_object_or_404(Fournisseur, pk=fournisseur_id)
            produit.nom = nom
            produit.description = description
            produit.prixUnitaire = prixUnitaire
            produit.fournisseur = fournisseur
            produit.save()
            messages.success(request, 'Produit updated successfully')
            return redirect('Products')
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'Products/edit_produit.html', {'produit': produit, 'fournisseurs': fournisseurs, 'values': produit})
@login_required
def delete_produit(request, id):
    produit = get_object_or_404(Produit, pk=id)
    produit.delete()
    messages.success(request, 'Produit removed')
    return redirect('Products')

@login_required
def stats_view(request):
    return render(request, 'stats.html')
@login_required
def delete_facture(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    facture.delete()
    messages.success(request, 'Facture deleted successfully')
    return redirect('facture_list')
@login_required
def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    data = [
        ['Field', 'Value'],
        ['Client', facture.client.nom],
        ['Date', facture.date.strftime('%Y-%m-%d')],
        ['Amount', f'{facture.montant}'],
        ['Status', facture.statut],
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.pk}.pdf"'
    return response

@login_required
def list_commandes(request):
    # Use prefetch_related to get all related products for each Commande
    commandes = Commande.objects.prefetch_related('commandeproduits__produit').all()
    return render(request, 'commandes/list.html', {'commandes': commandes})
@login_required
def update_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        if form.is_valid():
            form.save()
            return redirect('list_commandes')
    else:
        form = CommandeForm(instance=commande)
    return render(request, 'commandes/form.html', {'form': form})

@login_required
def delete_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        commande.delete()
        return redirect('list_commandes')
    return render(request, 'commandes/confirm_delete.html', {'commande': commande})
@login_required
def export_commandes_to_excel(request):
    # Create a workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Commandes'

    # Define the headers
    headers = ['Numero', 'Fournisseur', 'Date', 'Produits', 'Montant']
    worksheet.append(headers)

    # Fetch the data
    commandes = Commande.objects.prefetch_related('commandeproduits__produit').all()

    for commande in commandes:
        products = ', '.join(cp.produit.nom for cp in commande.commandeproduits.all())
        row = [
            commande.numero,
            commande.fournisseur.nom_societe,
            commande.date,
            products,
            commande.montant,
        ]
        worksheet.append(row)

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="commandes list.xlsx"'
    workbook.save(response)
    return response
@login_required
def create_or_update_commande(request, pk=None):
    if pk:
        commande = get_object_or_404(Commande, pk=pk)
    else:
        commande = Commande()

    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.fournisseur = get_object_or_404(Fournisseur, pk=request.POST.get('fournisseur'))
            commande.save()
            
            # Clear existing CommandeProduit entries and add new ones
            CommandeProduit.objects.filter(commande=commande).delete()
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            for product_id, quantity in zip(products, quantities):
                product = get_object_or_404(Produit, pk=product_id)
                CommandeProduit.objects.create(
                    commande=commande,
                    produit=product,
                    quantite=int(quantity)
                )

            return redirect('list_commandes')
    else:
        form = CommandeForm(instance=commande)

    fournisseurs = Fournisseur.objects.all()
    produits = Produit.objects.all()

    return render(request, 'commandes/form.html', {
        'form': form,
        'fournisseurs': fournisseurs,
        'produits': produits,
        'commande': commande,
    })

def fetch_products(request, fournisseur_id):
    products = Produit.objects.filter(fournisseur_id=fournisseur_id)
    product_data = [{"id": product.id, "nom": product.nom, "prixUnitaire": product.prixUnitaire} for product in products]
    return JsonResponse({"products": product_data})

@login_required      
def check_numero(request):
    numero = request.GET.get('numero', '')
    exists = Commande.objects.filter(numero=numero).exists()
    return JsonResponse({'exists': exists})
@login_required
def export_commandes_to_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Title
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title = Paragraph("Commandes Report", title_style)
    elements.append(title)

    # Headers and Data
    data = [['Numero', 'Fournisseur', 'Date', 'Products', 'Montant']]
    commandes = Commande.objects.prefetch_related('commandeproduits__produit').all()
    
    for commande in commandes:
        products = ', '.join(cp.produit.nom for cp in commande.commandeproduits.all())
        row = [
            commande.numero,
            commande.fournisseur.nom_societe,
            commande.date,
            products,
            commande.montant,
        ]
        data.append(row)
    
    # Create a table and style it
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="commandes_report.pdf"'
    return response

from django.views.generic import ListView, CreateView, DetailView
class FactureListView(LoginRequiredMixin,ListView):
    model = Facture
    template_name = 'factures/list.html'
    context_object_name = 'factures'

    def get_queryset(self):
        queryset = Facture.objects.all()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(numero__icontains=search_query) |
                Q(fournisseur__nom_societe__icontains=search_query)
            )
        return queryset

class FactureCreateView(LoginRequiredMixin,CreateView):
    model = Facture
    form_class = FactureForm
    template_name = 'factures/form.html'
    success_url = reverse_lazy('facture_list')

    def form_valid(self, form):
        # handle file upload
        if 'fichier' in self.request.FILES:
            form.instance.fichier = self.request.FILES['fichier']
        return super().form_valid(form)

class FactureDetailView(LoginRequiredMixin,DetailView):
    model = Facture
    template_name = 'factures/facture_detail.html'
    context_object_name = 'facture'
    
@login_required  
@require_POST
def update_facture_state(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    new_state = request.POST.get('state')

    # Ensure the new_state is in STATUT_CHOICES
    valid_states = dict(Facture.STATUT_CHOICES).keys()
    if new_state in valid_states:
        facture.state = new_state
        facture.save()

    return redirect('facture_list')    
def delete_facture(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, 'Facture deleted successfully.')
    return redirect('facture_list')

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from smtplib import SMTPAuthenticationError
from django.shortcuts import render, redirect
import logging

# Setup logging
logger = logging.getLogger(__name__)

def register_superuser(request):
    if request.method == 'POST':
        form = SuperUserCreationForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid. Proceeding with user creation.")
            # Save the user
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')

            # Send an email with username and password
            subject = 'Your Account Details'
            message = f'Hello {username},\n\nYour account has been created successfully.\n\nUsername: {username}\nPassword: {password}\n\nPlease keep this information secure.'
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            try:
                send_mail(subject, message, email_from, recipient_list)
                messages.success(request, "Superuser created and email sent successfully.")
                logger.debug("Email sent successfully.")
            except SMTPAuthenticationError as e:
                # Catch the SMTPAuthenticationError and show it as a pop-up
                error_message = f"Failed to send email: {e}"
                messages.error(request, error_message)
                logger.error(f"Email sending failed: {e}")
                return render(request, 'accounts/register_superuser.html', {'form': form})
            except Exception as e:
                # Catch all other exceptions
                error_message = f"An error occurred: {e}"
                messages.error(request, error_message)
                logger.error(f"An unexpected error occurred: {e}")
                return render(request, 'accounts/register_superuser.html', {'form': form})
            
            return redirect('polls')  # Redirect to the desired page after registration
        else:
            logger.debug("Form is invalid. Errors: %s", form.errors)
            messages.error(request, f"There was an error in your form submission: {form.errors}")
    else:
        form = SuperUserCreationForm()
    
    return render(request, 'accounts/register_superuser.html', {'form': form})

def dashboard_view(request):
    # Fetch data for dashboard
    total_factures = Facture.objects.count()
    total_commandes = Commande.objects.count()
    total_fournisseurs = Fournisseur.objects.count()
    total_invoices = Invoice.objects.count()  # Fetch total invoices

    # Calculate paid and unpaid invoices
    paid_invoices = Invoice.objects.filter(paid=True).count()
    unpaid_invoices = Invoice.objects.filter(paid=False).count()

    # Ensure the state values match what is used in your model
    paid_invoices_Axians = Facture.objects.filter(state='paid').count()
    unpaid_invoices_Axians = Facture.objects.filter(state='unpaid').count()

    context = {
        'total_factures': total_factures,
        'total_commandes': total_commandes,
        'total_fournisseurs': total_fournisseurs,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'paid_invoices_Axians': paid_invoices_Axians,
        'unpaid_invoices_Axians': unpaid_invoices_Axians,
    }
    return render(request, 'dashboard/dashboard.html', context)
