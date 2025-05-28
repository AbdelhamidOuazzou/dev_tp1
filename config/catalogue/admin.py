from django.contrib import admin
from .models import Destination, Circuit, OptionSupplement, Reservation, ReservationOption, Paiement

class OptionSupplementInline(admin.TabularInline):
    model = OptionSupplement
    extra = 1

class CircuitInline(admin.TabularInline):
    model = Circuit
    extra = 1
    show_change_link = True

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)
    inlines = [CircuitInline]
    actions = ['delete_selected']

    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'

@admin.register(Circuit)
class CircuitAdmin(admin.ModelAdmin):
    list_display = ('titre', 'destination', 'date_depart', 'duree', 'prix_base', 'places_disponibles')
    list_filter = ('destination', 'date_depart')
    search_fields = ('titre', 'destination__nom')
    date_hierarchy = 'date_depart'
    inlines = [OptionSupplementInline]
    actions = ['delete_selected']

@admin.register(OptionSupplement)
class OptionSupplementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'prix')
    search_fields = ('nom',)
    actions = ['delete_selected']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'circuit', 'client', 'date_reservation', 'statut', 'prix_total')
    list_filter = ('statut', 'date_reservation', 'circuit__destination')
    search_fields = ('client__username', 'circuit__titre')
    date_hierarchy = 'date_reservation'

@admin.register(ReservationOption)
class ReservationOptionAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'option', 'quantite', 'prix_unitaire')
    list_filter = ('option',)

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'reservation', 'montant', 'date_paiement', 'statut')
    list_filter = ('statut', 'date_paiement', 'type_paiement')
    search_fields = ('numero_facture', 'reservation__client__username')
    date_hierarchy = 'date_paiement'
