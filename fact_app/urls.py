from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('polls/', views.index, name='polls'),
    path('en/add_fournisseur/', views.add_fournisseur, name='add_fournisseur'),
    path('en/edit_fournisseur/<int:id>/', views.edit_fournisseur, name='edit_fournisseur'),
    path('en/delete_fournisseur/<int:id>/', views.delete_fournisseur, name='delete_fournisseur'),
    path('<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),
    path('en/fournisseur/<int:fournisseur_id>/add-produit/', views.add_produit_fournisseurs, name='add_produit_fournisseurs'),
    path('Product/', views.Products, name='Products'),
    path('en/add_produit/', views.add_produit, name='add_produit'),
    path('en/edit_produit/<int:id>/', views.edit_produit, name='edit_produit'),
    path('en/delete_produit/<int:id>/', views.delete_produit, name='delete_produit'),
    path('en/commandes/', views.list_commandes, name='list_commandes'),
    path('en/commandes/create/', views.create_or_update_commande, name='create_commande'),
    path('en/commandes/update/<int:pk>/', views.update_commande, name='update_commande'),
    path('en/commandes/delete/<int:pk>/', views.delete_commande, name='delete_commande'),
    path('fetch-products/<int:fournisseur_id>/', views.fetch_products, name='fetch-products'),
    path('check_numero/', views.check_numero, name='check_numero'),
    path('en/export_commandes/', views.export_commandes_to_excel, name='export_commandes'),
    path('en/export_commandes_pdf/', views.export_commandes_to_pdf, name='export_commandes_pdf'),
    path('factures/', views.FactureListView.as_view(), name='facture_list'),
    path('factures/add/', views.FactureCreateView.as_view(), name='create_facture'),
    path('factures/<int:pk>/', views.FactureDetailView.as_view(), name='view_facture'),
    path('facture/<int:pk>/update_state/', views.update_facture_state, name='update_facture_state'),
    path('facture/<int:pk>/delete/', views.delete_facture, name='delete_facture'),
    #  path('metrics/', exports.ExportToDjangoPrometheus(), name='prometheus-metrics'),
    # path('metrics/', metrics_view, name='prometheus-metrics'),  
    path('HomeView', views.HomeView.as_view(), name='home'),
    path('add-customer', views.AddCustomerView.as_view(), name='add_customer'),
    path('add-invoice', views.AddInvoiceView.as_view(), name='add-invoice'),
    #  path('add-invoice/', views.AddCustomerInvoiceView.as_view(), name='add_invoice'),
    path('view-invoice/<int:pk>', views.InvoiceVisualizationView.as_view(), name='view-invoice'),
    path('invoice-pdf/<int:pk>', views.get_invoice_pdf, name="invoice-pdf"),
    path('register-superuser/', views.register_superuser, name='register_superuser'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

