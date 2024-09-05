from django.contrib import admin
from .models import Article, Client, Invoice, Produit
from django.utils.translation import gettext_lazy as _

class AdminCustomer(admin.ModelAdmin):
    list_display = ('nom_societe','name', 'email', 'phone', 'address','city','Pays','zip_code')

class AdminInvoice(admin.ModelAdmin):
    list_display = ('customer', 'save_by', 'invoice_date_time', 'total', 'last_updated_date', 'paid')    

admin.site.register(Client, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Article)

admin.site.site_title = _("AXIANS IT SOLUTION SYSTEM")
admin.site.site_header = _("AXIANS IT SOLUTION")
admin.site.index_title = _("AXIANS IT SOLUTION")