from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count, Avg, FloatField, F, Max
from django.db.models.functions import Cast, TruncMonth
from .models import Destination, Circuit, OptionSupplement, Reservation, ReservationOption, Paiement, CircuitAvailability, Communication, Rapport, Notification
from .forms import DestinationForm, CircuitForm, OptionSupplementForm, ReservationForm, PaiementForm, CircuitAvailabilityForm, CommunicationForm, RapportForm
from accounts.models import User
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, timezone as dt_timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import csv
import xlsxwriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.template.loader import render_to_string
import json
from xhtml2pdf import pisa
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token as get_csrf_token
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_admin_user()

def is_sub_admin(user):
    return user.is_sub_admin()

def is_admin_or_sub_admin(user):
    return user.is_admin_user() or user.is_sub_admin()

def is_agent(user):
    return user.is_agent()

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_dashboard(request):
    destinations = Destination.objects.all()
    circuits = Circuit.objects.all()
    options = OptionSupplement.objects.all()
    
    return render(request, 'catalogue/sub_admin/dashboard.html', {
        'destinations': destinations,
        'circuits': circuits,
        'options': options,
    })

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'catalogue/sub_admin/destination_list.html', {'destinations': destinations})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_destination_create(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination created successfully.')
            return redirect('sub_admin_destination_list')
    else:
        form = DestinationForm()
    return render(request, 'catalogue/sub_admin/destination_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_destination_edit(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination mise à jour avec succès!')
            return redirect('sub_admin_destination_list')
    else:
        form = DestinationForm(instance=destination)
    return render(request, 'catalogue/sub_admin/destination_form.html', {'form': form, 'destination': destination})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_destination_delete(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        try:
            destination_name = destination.nom
            destination.delete()
            messages.success(request, f'Destination "{destination_name}" supprimée avec succès!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_circuit_list(request):
    circuits = Circuit.objects.select_related('destination').all()
    return render(request, 'catalogue/sub_admin/circuit_list.html', {'circuits': circuits})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_circuit_create(request):
    if request.method == 'POST':
        form = CircuitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Circuit created successfully.')
            return redirect('sub_admin_circuit_list')
    else:
        form = CircuitForm()
    return render(request, 'catalogue/sub_admin/circuit_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_circuit_edit(request, pk):
    circuit = get_object_or_404(Circuit, pk=pk)
    if request.method == 'POST':
        form = CircuitForm(request.POST, instance=circuit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Circuit mis à jour avec succès!')
            return redirect('sub_admin_circuit_list')
    else:
        form = CircuitForm(instance=circuit)
    return render(request, 'catalogue/sub_admin/circuit_form.html', {'form': form, 'circuit': circuit})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_circuit_delete(request, pk):
    circuit = get_object_or_404(Circuit, pk=pk)
    if request.method == 'POST':
        try:
            circuit_name = circuit.titre
            circuit.delete()
            messages.success(request, f'Circuit "{circuit_name}" supprimé avec succès!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    destinations = Destination.objects.all()
    circuits = Circuit.objects.all()
    options = OptionSupplement.objects.all()
    
    return render(request, 'catalogue/admin/dashboard.html', {
        'destinations': destinations,
        'circuits': circuits,
        'options': options
    })

@login_required
@user_passes_test(is_admin)
def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'catalogue/admin/destination_list.html', {'destinations': destinations})

@login_required
@user_passes_test(is_admin)
def destination_create(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination créée avec succès!')
            return redirect('admin_destination_list')
    else:
        form = DestinationForm()
    return render(request, 'catalogue/admin/destination_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def destination_edit(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination mise à jour avec succès!')
            return redirect('admin_destination_list')
    else:
        form = DestinationForm(instance=destination)
    return render(request, 'catalogue/admin/destination_form.html', {'form': form, 'destination': destination})

@login_required
@user_passes_test(is_admin)
def destination_delete(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        destination.delete()
        messages.success(request, 'Destination supprimée avec succès!')
        return redirect('admin_destination_list')
    return render(request, 'catalogue/admin/destination_confirm_delete.html', {'destination': destination})

@login_required
@user_passes_test(is_admin)
def circuit_list(request):
    circuits = Circuit.objects.select_related('destination').all()
    return render(request, 'catalogue/admin/circuit_list.html', {'circuits': circuits})

@login_required
@user_passes_test(is_admin)
def circuit_create(request):
    if request.method == 'POST':
        form = CircuitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Circuit créé avec succès!')
            return redirect('admin_circuit_list')
    else:
        form = CircuitForm()
    return render(request, 'catalogue/admin/circuit_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def circuit_edit(request, pk):
    circuit = get_object_or_404(Circuit, pk=pk)
    if request.method == 'POST':
        form = CircuitForm(request.POST, instance=circuit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Circuit mis à jour avec succès!')
            return redirect('admin_circuit_list')
    else:
        form = CircuitForm(instance=circuit)
    return render(request, 'catalogue/admin/circuit_form.html', {'form': form, 'circuit': circuit})

@login_required
@user_passes_test(is_admin)
def circuit_delete(request, pk):
    circuit = get_object_or_404(Circuit, pk=pk)
    if request.method == 'POST':
        circuit.delete()
        messages.success(request, 'Circuit supprimé avec succès!')
        return redirect('admin_circuit_list')
    return render(request, 'catalogue/admin/circuit_confirm_delete.html', {'circuit': circuit})

@login_required
@user_passes_test(is_admin)
def option_list(request):
    options = OptionSupplement.objects.select_related('circuit__destination').all()
    return render(request, 'catalogue/admin/option_list.html', {'options': options})

@login_required
@user_passes_test(is_admin)
def option_create(request):
    if request.method == 'POST':
        form = OptionSupplementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Option créée avec succès!')
            return redirect('admin_option_list')
    else:
        form = OptionSupplementForm()
    return render(request, 'catalogue/admin/option_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def option_edit(request, pk):
    option = get_object_or_404(OptionSupplement, pk=pk)
    if request.method == 'POST':
        form = OptionSupplementForm(request.POST, instance=option)
        if form.is_valid():
            form.save()
            messages.success(request, 'Option mise à jour avec succès!')
            return redirect('admin_option_list')
    else:
        form = OptionSupplementForm(instance=option)
    return render(request, 'catalogue/admin/option_form.html', {'form': form, 'option': option})

@login_required
@user_passes_test(is_admin)
def option_delete(request, pk):
    option = get_object_or_404(OptionSupplement, pk=pk)
    if request.method == 'POST':
        option.delete()
        messages.success(request, 'Option supprimée avec succès!')
        return redirect('admin_option_list')
    return render(request, 'catalogue/admin/option_confirm_delete.html', {'option': option})

def catalogue(request):
    circuits = Circuit.objects.select_related('destination').all()
    return render(request, 'catalogue/catalogue.html', {'circuits': circuits})

def circuit_detail(request, id):
    circuit = get_object_or_404(Circuit, id=id)
    form = ReservationForm(circuit=circuit)
    return render(request, 'catalogue/circuit_detail.html', {
        'circuit': circuit,
        'form': form
    })

@login_required
def reserver_circuit(request, circuit_id):
    circuit = get_object_or_404(Circuit, id=circuit_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, circuit=circuit)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create and save the reservation first
                    reservation = form.save(commit=False)
                    reservation.client = request.user
                    reservation.circuit = circuit
                    reservation.prix_total = circuit.prix_base * reservation.nombre_voyageurs
                    reservation.save()
                    
                    # Update available places
                    circuit.places_disponibles -= reservation.nombre_voyageurs
                    circuit.save()
                    
                    messages.success(request, 'Votre réservation a été créée avec succès!')
                    return redirect('reservation_list')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de la création de la réservation: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ReservationForm(circuit=circuit)
    
    return render(request, 'catalogue/circuit_detail.html', {
        'circuit': circuit,
        'form': form
    })

@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, client=request.user)
    paiements = reservation.paiements.all().order_by('-date_paiement')
    
    return render(request, 'catalogue/reservation_detail.html', {
        'reservation': reservation,
        'paiements': paiements
    })

@login_required
def reservation_list(request):
    reservations = Reservation.objects.filter(client=request.user).order_by('-date_reservation')
    return render(request, 'catalogue/reservation_list.html', {
        'reservations': reservations
    })

@login_required
def paiement_create(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    
    # Calculate payment totals
    total_paid = reservation.paiements.filter(statut='complete').aggregate(total=Sum('montant'))['total'] or 0
    remaining_amount = reservation.prix_total - total_paid
    
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.reservation = reservation
            paiement.statut = 'complete'  # Set initial status as complete
            paiement.save()
            
            messages.success(request, 'Le paiement a été enregistré avec succès.')
            return redirect('sub_admin_reservation_detail', pk=reservation.pk)
    else:
        form = PaiementForm(initial={'reservation': reservation})
    
    context = {
        'reservation': reservation,
        'form': form,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
    }
    
    return render(request, 'catalogue/sub_admin/paiement_form.html', context)

@login_required
def paiement_simuler(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id, reservation__client=request.user)
    
    if request.method == 'POST':
        paiement.statut = 'complete'
        paiement.save()
        
        # Vérifier si la réservation est entièrement payée
        montant_total = paiement.reservation.prix_total
        montant_paye = sum(p.montant for p in paiement.reservation.paiements.filter(statut='complete'))
        
        if montant_paye >= montant_total:
            paiement.reservation.statut = 'confirmee'
            paiement.reservation.save()
        
        messages.success(request, 'Paiement simulé avec succès!')
        return redirect('reservation_detail', pk=paiement.reservation.pk)
    
    return render(request, 'catalogue/paiement_simuler.html', {
        'paiement': paiement
    })

# Admin views for reservations
@login_required
def admin_reservation_list(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Accès non autorisé.')
        return redirect('catalogue')
    
    reservations = Reservation.objects.all().order_by('-date_reservation')
    return render(request, 'catalogue/admin/reservation_list.html', {
        'reservations': reservations
    })

@login_required
def admin_reservation_detail(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Accès non autorisé.')
        return redirect('catalogue')
    
    reservation = get_object_or_404(Reservation, pk=pk)
    paiements = reservation.paiements.all().order_by('-date_paiement')
    
    return render(request, 'catalogue/admin/reservation_detail.html', {
        'reservation': reservation,
        'paiements': paiements
    })

@login_required
def admin_reservation_update(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Accès non autorisé.')
        return redirect('catalogue')
    
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if request.method == 'POST':
        statut = request.POST.get('statut')
        if statut in dict(Reservation.STATUT_CHOICES):
            reservation.statut = statut
            reservation.save()
            messages.success(request, 'Statut de la réservation mis à jour.')
            return redirect('admin_reservation_detail', pk=reservation.pk)
    
    return render(request, 'catalogue/admin/reservation_update.html', {
        'reservation': reservation
    })

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_option_create(request):
    if request.method == 'POST':
        form = OptionSupplementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplementary option created successfully.')
            return redirect('sub_admin_option_list')
    else:
        form = OptionSupplementForm()
    return render(request, 'catalogue/sub_admin/option_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_option_list(request):
    options = OptionSupplement.objects.all()
    return render(request, 'catalogue/sub_admin/option_list.html', {'options': options})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_option_edit(request, pk):
    option = get_object_or_404(OptionSupplement, pk=pk)
    if request.method == 'POST':
        form = OptionSupplementForm(request.POST, instance=option)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplementary option updated successfully.')
            return redirect('sub_admin_option_list')
    else:
        form = OptionSupplementForm(instance=option)
    return render(request, 'catalogue/sub_admin/option_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_option_delete(request, pk):
    option = get_object_or_404(OptionSupplement, pk=pk)
    if request.method == 'POST':
        option.delete()
        messages.success(request, 'Supplementary option deleted successfully.')
        return redirect('sub_admin_option_list')
    return render(request, 'catalogue/sub_admin/option_confirm_delete.html', {'option': option})

@login_required
def dashboard(request):
    if request.user.role != 'sub_admin':
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('catalogue')
    
    destinations = Destination.objects.all()
    circuits = Circuit.objects.all()
    options = OptionSupplement.objects.all()
    
    context = {
        'destinations': destinations,
        'circuits': circuits,
        'options': options,
    }
    return render(request, 'catalogue/dashboard.html', context)

@login_required
@user_passes_test(is_agent)
def agent_dashboard(request):
    # Get all reservations
    all_reservations = Reservation.objects.select_related('circuit', 'client').all().order_by('-date_reservation')
    
    # Filter reservations by status
    pending_reservations = all_reservations.filter(statut='en_attente')
    confirmed_reservations = all_reservations.filter(statut='confirmee')
    cancelled_reservations = all_reservations.filter(statut='annulee')
    
    # Get statistics
    total_reservations = all_reservations.count()
    total_circuits = Circuit.objects.count()
    total_clients = User.objects.filter(is_staff=False).count()
    total_revenue = all_reservations.filter(statut='confirmee').aggregate(
        total=Sum('prix_total')
    )['total'] or 0
    
    # Get recent reservations (last 5)
    recent_reservations = all_reservations[:5]
    
    # Get popular circuits (top 5 by number of reservations)
    popular_circuits = Circuit.objects.annotate(
        reservation_count=Count('reservations')
    ).order_by('-reservation_count')[:5]
    
    context = {
        'current_date': timezone.now(),
        'total_reservations': total_reservations,
        'total_circuits': total_circuits,
        'total_clients': total_clients,
        'total_revenue': total_revenue,
        'recent_reservations': recent_reservations,
        'popular_circuits': popular_circuits,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'cancelled_reservations': cancelled_reservations,
    }
    
    return render(request, 'catalogue/agent/dashboard.html', context)

@login_required
@user_passes_test(is_agent)
def agent_reservation_list(request):
    status = request.GET.get('status')
    reservations = Reservation.objects.all()
    
    if status:
        reservations = reservations.filter(statut=status)
    
    reservations = reservations.order_by('-date_reservation')
    return render(request, 'catalogue/agent/reservation_list.html', {
        'reservations': reservations,
        'status': status
    })

@login_required
@user_passes_test(is_agent)
def agent_reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, 'catalogue/agent/reservation_detail.html', {
        'reservation': reservation
    })

@login_required
@user_passes_test(is_agent)
def agent_reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('statut')
        if not new_status:
            messages.error(request, 'Veuillez sélectionner un statut.')
            return render(request, 'catalogue/agent/reservation_update.html', {
                'reservation': reservation
            })
            
        if new_status in dict(Reservation.STATUT_CHOICES):
            old_status = reservation.statut
            reservation.statut = new_status
            reservation.save()
            
            # Send notification to client
            if new_status == 'confirmee':
                messages.success(request, 'La réservation a été confirmée.')
                # Send success message to client
                messages.success(request, f'Notification envoyée à {reservation.client.get_full_name()}.')
            elif new_status == 'annulee':
                messages.warning(request, 'La réservation a été annulée.')
                # Send warning message to client
                messages.warning(request, f'Notification envoyée à {reservation.client.get_full_name()}.')
            
            # Redirect back to the reservation detail page
            return redirect('agent_reservation_detail', pk=pk)
        else:
            messages.error(request, 'Statut invalide.')
    
    return render(request, 'catalogue/agent/reservation_update.html', {
        'reservation': reservation
    })

@login_required
@user_passes_test(is_agent)
def payment_management(request):
    paiements = Paiement.objects.select_related('reservation', 'reservation__client').all()
    return render(request, 'catalogue/agent/payment_management.html', {
        'paiements': paiements
    })

@login_required
@user_passes_test(is_agent)
def paiement_simuler(request):
    if request.method == 'POST':
        montant_total = float(request.POST.get('montant_total', 0))
        nombre_paiements = int(request.POST.get('nombre_paiements', 1))
        
        # Calculer les montants des paiements
        paiements = []
        if nombre_paiements == 1:
            paiements.append({
                'montant': montant_total,
                'date': 'À la réservation',
                'pourcentage': 100
            })
        elif nombre_paiements == 2:
            paiements.append({
                'montant': montant_total * 0.4,
                'date': 'À la réservation',
                'pourcentage': 40
            })
            paiements.append({
                'montant': montant_total * 0.6,
                'date': '30 jours avant le départ',
                'pourcentage': 60
            })
        elif nombre_paiements == 3:
            paiements.append({
                'montant': montant_total * 0.3,
                'date': 'À la réservation',
                'pourcentage': 30
            })
            paiements.append({
                'montant': montant_total * 0.4,
                'date': '30 jours avant le départ',
                'pourcentage': 40
            })
            paiements.append({
                'montant': montant_total * 0.3,
                'date': 'Le jour du départ',
                'pourcentage': 30
            })
        elif nombre_paiements == 4:
            paiements.append({
                'montant': montant_total * 0.25,
                'date': 'À la réservation',
                'pourcentage': 25
            })
            paiements.append({
                'montant': montant_total * 0.25,
                'date': '60 jours avant le départ',
                'pourcentage': 25
            })
            paiements.append({
                'montant': montant_total * 0.25,
                'date': '30 jours avant le départ',
                'pourcentage': 25
            })
            paiements.append({
                'montant': montant_total * 0.25,
                'date': 'Le jour du départ',
                'pourcentage': 25
            })
        
        return render(request, 'catalogue/agent/payment_simulation_result.html', {
            'montant_total': montant_total,
            'nombre_paiements': nombre_paiements,
            'paiements': paiements
        })
    
    return redirect('payment_management')

@login_required
@user_passes_test(is_agent)
def paiement_detail(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    return render(request, 'catalogue/agent/payment_detail.html', {
        'paiement': paiement
    })

@login_required
@user_passes_test(is_agent)
def paiement_edit(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        form = PaiementForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paiement mis à jour avec succès.')
            return redirect('payment_management')
    else:
        form = PaiementForm(instance=paiement)
    return render(request, 'catalogue/agent/payment_form.html', {
        'form': form,
        'paiement': paiement
    })

@login_required
@user_passes_test(is_agent)
def paiement_delete(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        paiement.delete()
        messages.success(request, 'Paiement supprimé avec succès.')
        return redirect('payment_management')
    return render(request, 'catalogue/agent/payment_confirm_delete.html', {
        'paiement': paiement
    })

# Availability Management Views
@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_availability(request):
    # Get filter parameters
    selected_circuit = request.GET.get('circuit')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset with optimizations
    circuits = Circuit.objects.select_related('destination').all()
    availabilities = CircuitAvailability.objects.select_related('circuit').all().order_by('date')
    
    # Apply filters
    if selected_circuit:
        availabilities = availabilities.filter(circuit_id=selected_circuit)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            availabilities = availabilities.filter(date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            availabilities = availabilities.filter(date__lte=date_to)
        except ValueError:
            pass
    
    # Calculate statistics
    total_places = availabilities.aggregate(
        total=Sum('places_disponibles')
    )['total'] or 0
    
    total_reservations = availabilities.aggregate(
        total=Sum('places_reservees')
    )['total'] or 0
    
    # Calculate occupation rate
    total_capacity = total_places + total_reservations
    occupation_rate = round((total_reservations / total_capacity * 100) if total_capacity > 0 else 0, 1)
    
    # Handle form submission for adding availability
    if request.method == 'POST':
        form = CircuitAvailabilityForm(request.POST)
        if form.is_valid():
            try:
                # Check if availability already exists for this circuit and date
                circuit = form.cleaned_data['circuit']
                date = form.cleaned_data['date']
                existing = CircuitAvailability.objects.filter(circuit=circuit, date=date).first()
                
                if existing:
                    messages.error(request, 'Une disponibilité existe déjà pour ce circuit à cette date.')
                else:
                    # Create new availability
                    availability = form.save()
                    messages.success(request, f'Disponibilité ajoutée avec succès pour {circuit.titre} le {date.strftime("%d/%m/%Y")}.')
                    return redirect('sub_admin_availability')
            except Exception as e:
                messages.error(request, f'Erreur lors de la sauvegarde: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = CircuitAvailabilityForm()
    
    # Prepare calendar events
    calendar_events = []
    for availability in availabilities:
        # Determine status class based on available places
        if availability.places_disponibles > 10:
            status_class = 'status-available'
            status_text = 'Disponible'
        elif availability.places_disponibles > 0:
            status_class = 'status-limited'
            status_text = 'Places limitées'
        else:
            status_class = 'status-full'
            status_text = 'Complet'
            
        calendar_events.append({
            'id': availability.id,
            'title': f"{availability.circuit.titre} ({availability.places_disponibles} places)",
            'start': availability.date.isoformat(),
            'className': status_class,
            'extendedProps': {
                'circuit_id': availability.circuit_id,
                'circuit_name': availability.circuit.titre,
                'places_disponibles': availability.places_disponibles,
                'places_reservees': availability.places_reservees,
                'status': status_text
            }
        })
    
    context = {
        'circuits': circuits,
        'availabilities': availabilities,
        'form': form,
        'selected_circuit': selected_circuit,
        'date_from': date_from,
        'date_to': date_to,
        'total_places': total_places,
        'total_reservations': total_reservations,
        'occupation_rate': occupation_rate,
        'calendar_events': calendar_events,
    }
    
    return render(request, 'catalogue/sub_admin/availability.html', context)

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_availability_delete(request, pk):
    """View to handle availability deletion"""
    availability = get_object_or_404(CircuitAvailability, pk=pk)
    
    if request.method == 'POST':
        try:
            circuit_name = availability.circuit.titre
            date = availability.date
            availability.delete()
            messages.success(request, f'Disponibilité supprimée avec succès pour {circuit_name} le {date.strftime("%d/%m/%Y")}.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

# Communication Views
@login_required
def sub_admin_communication(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            message = data.get('message')

            if not user_id or not message:
                return JsonResponse({
                    'success': False,
                    'message': 'Tous les champs sont requis'
                }, status=400)

            # Validate message length
            if len(message.strip()) == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Le message ne peut pas être vide'
                }, status=400)

            if len(message) > 1000:  # Maximum message length
                return JsonResponse({
                    'success': False,
                    'message': 'Le message est trop long (maximum 1000 caractères)'
                }, status=400)

            # Get the recipient user
            try:
                recipient = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }, status=404)
            
            # Create communication record with transaction
            try:
                with transaction.atomic():
                    # Create the communication record
                    communication = Communication.objects.create(
                        type='message',
                        sujet='Message direct',
                        message=message.strip(),
                        destinataire=recipient,
                        expediteur=request.user,
                        date_creation=timezone.now(),
                        date_envoi=timezone.now(),
                        statut='envoye',
                        lu=False,
                        reservation=None
                    )

                    # Create notification for the recipient
                    Notification.objects.create(
                        destinataire=recipient,
                        type='systeme',
                        titre='Nouveau message',
                        message=f'Vous avez reçu un nouveau message de {request.user.get_full_name()}',
                        lien=f'/communication/{request.user.id}/',
                        priorite='normale'
                    )

                    # Format the response message
                    formatted_message = {
                        'id': communication.id,
                        'content': communication.message,
                        'time': communication.date_creation.strftime('%H:%M'),
                        'date': communication.date_creation.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'sent',
                        'is_sent': True
                    }

                    # Add CSRF token to response headers
                    response = JsonResponse({
                        'success': True,
                        'message': formatted_message
                    })
                    response['X-CSRFToken'] = get_csrf_token(request)
                    return response

            except Exception as e:
                # Log the error for debugging
                print(f"Error creating communication: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la création du message: {str(e)}'
                }, status=500)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Format de données invalide'
            }, status=400)
        except Exception as e:
            # Log the error for debugging
            print(f"Unexpected error in sub_admin_communication: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de l\'envoi du message: {str(e)}'
            }, status=500)

    # For GET requests, return a new CSRF token
    response = render(request, 'catalogue/sub_admin/communication.html', {
        'users': User.objects.filter(
            Q(is_staff=False) | Q(id=request.user.id)
        ).exclude(id=request.user.id).annotate(
            unread_count=Count('communications_recues', filter=Q(
                communications_recues__lu=False,
                communications_recues__expediteur=request.user
            )),
            last_message=Max('communications_recues__date_creation', filter=Q(
                Q(communications_recues__expediteur=request.user) |
                Q(communications_recues__destinataire=request.user)
            ))
        ).order_by('-last_message', '-unread_count', 'username')
    })
    response['X-CSRFToken'] = get_csrf_token(request)
    return response

@login_required
def get_user_messages(request, user_id):
    try:
        other_user = get_object_or_404(User, id=user_id, is_active=True)
        
        # Get messages between current user and other user
        messages = Communication.objects.filter(
            Q(expediteur=request.user, destinataire=other_user) |
            Q(expediteur=other_user, destinataire=request.user)
        ).select_related('expediteur', 'destinataire').order_by('date_creation')

        # Mark messages from other user as read
        unread_messages = messages.filter(
            expediteur=other_user, 
            lu=False,
            date_envoi__isnull=False  # Only mark messages that have been sent
        )
        
        if unread_messages.exists():
            now = timezone.now()
            unread_messages.update(lu=True)

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            # Determine message status
            if msg.expediteur == request.user:
                if msg.date_envoi is None:
                    status = 'sending'
                elif msg.lu:
                    status = 'read'
                else:
                    status = 'sent'
            else:
                status = 'received'

            formatted_messages.append({
                'id': msg.id,
                'content': msg.message,
                'time': msg.date_creation.strftime('%H:%M'),
                'date': msg.date_creation.strftime('%Y-%m-%d %H:%M:%S'),
                'is_sent': msg.expediteur == request.user,
                'status': status,
                'sender_name': msg.expediteur.get_full_name() or msg.expediteur.username,
                'recipient_name': msg.destinataire.get_full_name() or msg.destinataire.username
            })

        return JsonResponse({
            'success': True,
            'messages': formatted_messages,
            'user_info': {
                'id': other_user.id,
                'name': other_user.get_full_name() or other_user.username,
                'is_online': True,  # Replace with actual online status
                'last_seen': other_user.last_login.strftime('%H:%M') if other_user.last_login else None
            }
        })

    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Utilisateur non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la récupération des messages: {str(e)}'
        }, status=500)

@login_required
def mark_messages_read(request, user_id):
    try:
        other_user = get_object_or_404(User, id=user_id)
        
        # Mark all messages from other user as read
        Communication.objects.filter(
            expediteur=other_user,
            destinataire=request.user,
            lu=False
        ).update(lu=True)

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def send_typing_status(request, user_id):
    try:
        recipient = get_object_or_404(User, id=user_id)
        
        # Create a temporary notification for typing status
        notification = Notification.objects.create(
            user=recipient,
            type='system',  # Changed from 'typing' to 'system' which is a valid type
            titre='En train d\'écrire',
            message=f'{request.user.get_full_name()} est en train d\'écrire...',
            lien=f'/communication/{request.user.id}/',
            priorite='basse'  # Added priority
        )
        
        # Delete the notification after 3 seconds
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Q
        
        # Clean up old typing notifications
        Notification.objects.filter(
            Q(type='system') & 
            Q(titre='En train d\'écrire') & 
            Q(date_creation__lt=timezone.now() - timedelta(seconds=5))
        ).delete()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin_or_sub_admin)
def get_user_reservations(request, user_id):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            user = User.objects.get(id=user_id, is_active=True)
            reservations = Reservation.objects.filter(
                client=user
            ).select_related('circuit').order_by('-date_creation')

            reservations_data = [{
                'id': r.id,
                'circuit': r.circuit.titre,
                'date': r.date_creation.strftime('%d/%m/%Y'),
                'status': r.get_statut_display(),
                'status_color': {
                    'confirmee': 'success',
                    'en_attente': 'warning',
                    'annulee': 'danger'
                }.get(r.statut, 'secondary')
            } for r in reservations]

            return JsonResponse({
                'success': True,
                'reservations': reservations_data
            })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Utilisateur non trouvé'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def mark_communication_read(request, communication_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            communication = Communication.objects.get(id=communication_id)
            communication.lu = True
            communication.save()
            return JsonResponse({'success': True})
        except Communication.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Communication non trouvée'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def mark_all_communications_read(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            Communication.objects.filter(lu=False).update(lu=True)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
@user_passes_test(is_admin_or_sub_admin)
def get_reservation_client(request, reservation_id):
    """AJAX view to get client information for a reservation"""
    try:
        reservation = get_object_or_404(Reservation.objects.select_related('client'), pk=reservation_id)
        return JsonResponse({
            'success': True,
            'client': {
                'id': reservation.client.id,
                'name': reservation.client.get_full_name(),
                'email': reservation.client.email,
                'phone': getattr(reservation.client, 'telephone', '')
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@user_passes_test(is_admin_or_sub_admin)
def resend_communication(request, pk):
    """View to resend a failed communication"""
    if request.method == 'POST':
        try:
            communication = get_object_or_404(Communication, pk=pk)
            
            # Here you would typically integrate with your email/SMS service
            # For now, we'll just update the status
            communication.statut = 'envoye'
            communication.date_envoi = timezone.now()
            communication.save()
            
            messages.success(request, 'Message renvoyé avec succès.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

# Reports Views
@login_required
def sub_admin_reports(request):
    """View for generating and displaying reports."""
    if not request.user.is_sub_admin:
        raise PermissionDenied("Vous n'avez pas les droits nécessaires pour accéder à cette page.")
    
    # Get date range from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = timezone.now().strftime('%Y-%m-%d')
    
    # Convert to datetime objects with UTC timezone
    date_from = datetime.strptime(date_from, '%Y-%m-%d').replace(tzinfo=dt_timezone.utc)
    date_to = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=dt_timezone.utc)
    
    # Get all reservations within date range
    reservations = Reservation.objects.filter(
        date_reservation__range=(date_from, date_to)
    ).select_related('circuit', 'client')
    
    # Calculate statistics
    total_sales = reservations.aggregate(total=Sum('prix_total'))['total'] or 0
    total_reservations = reservations.count()
    
    # Sales by circuit
    sales_by_circuit = reservations.values('circuit__titre').annotate(
        total_sales=Sum('prix_total'),
        reservation_count=Count('id'),
        avg_price=Avg('prix_total')
    ).order_by('-total_sales')
    
    # Monthly sales evolution
    monthly_sales = reservations.annotate(
        month=TruncMonth('date_reservation')
    ).values('month').annotate(
        total=Sum('prix_total')
    ).order_by('month')
    
    # Circuit occupancy
    circuits = Circuit.objects.all()
    total_places = sum(circuit.places_disponibles for circuit in circuits)
    total_reserved = reservations.aggregate(total=Sum('nombre_voyageurs'))['total'] or 0
    overall_occupancy_rate = (total_reserved / total_places * 100) if total_places > 0 else 0
    
    # Occupancy by circuit
    occupancy_by_circuit = []
    for circuit in circuits:
        circuit_reservations = reservations.filter(circuit=circuit)
        total_reserved = circuit_reservations.aggregate(total=Sum('nombre_voyageurs'))['total'] or 0
        occupancy_rate = (total_reserved / circuit.places_disponibles * 100) if circuit.places_disponibles > 0 else 0
        occupancy_by_circuit.append({
            'circuit__titre': circuit.titre,
            'total_places': circuit.places_disponibles,
            'total_reserved': total_reserved,
            'occupancy_rate': occupancy_rate
        })
    
    # Client statistics
    client_stats = reservations.values('client__username').annotate(
        total_spent=Sum('prix_total'),
        reservation_count=Count('id'),
        avg_spent=Avg('prix_total')
    ).order_by('-total_spent')[:10]
    
    # Handle form submission
    if request.method == 'POST':
        form = RapportForm(request.POST)
        if form.is_valid():
            try:
                rapport = form.save(commit=False)
                rapport.cree_par = request.user
                rapport.date_debut = date_from
                rapport.date_fin = date_to
                
                # Prepare report data based on type
                if rapport.type == 'ventes':
                    rapport.donnees = {
                        'total_sales': float(total_sales),
                        'total_reservations': total_reservations,
                        'sales_by_circuit': list(sales_by_circuit),
                        'monthly_sales': list(monthly_sales)
                    }
                elif rapport.type == 'occupation':
                    rapport.donnees = {
                        'overall_occupancy_rate': float(overall_occupancy_rate),
                        'total_places': total_places,
                        'total_reserved': total_reserved,
                        'occupancy_by_circuit': occupancy_by_circuit
                    }
                elif rapport.type == 'clients':
                    rapport.donnees = {
                        'client_stats': list(client_stats)
                    }
                
                rapport.save()
                
                # If it's an AJAX request, generate and return PDF directly
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    try:
                        # Create a BytesIO buffer to receive the PDF data
                        buffer = BytesIO()
                        
                        # Create PDF using ReportLab instead of xhtml2pdf
                        doc = SimpleDocTemplate(
                            buffer,
                            pagesize=letter,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=72
                        )
                        
                        # Create styles
                        styles = getSampleStyleSheet()
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Heading1'],
                            fontSize=16,
                            spaceAfter=30,
                            alignment=1  # Center alignment
                        )
                        
                        # Create elements list
                        elements = []
                        
                        # Add title
                        elements.append(Paragraph(f"Rapport {rapport.get_type_display()}", title_style))
                        elements.append(Spacer(1, 20))
                        
                        # Add report information
                        info_style = styles['Normal']
                        elements.append(Paragraph(f"Titre: {rapport.titre}", info_style))
                        elements.append(Paragraph(f"Date de création: {rapport.date_creation.strftime('%d/%m/%Y')}", info_style))
                        elements.append(Paragraph(f"Période: du {rapport.date_debut.strftime('%d/%m/%Y')} au {rapport.date_fin.strftime('%d/%m/%Y')}", info_style))
                        elements.append(Spacer(1, 20))
                        
                        # Add report content based on type
                        if rapport.type == 'ventes':
                            # Sales report content
                            data = [['Circuit', 'Total Ventes', 'Nombre Réservations', 'Prix Moyen']]
                            for sale in rapport.donnees['sales_by_circuit']:
                                data.append([
                                    sale['circuit__titre'],
                                    f"{sale['total_sales']:.2f} €",
                                    str(sale['reservation_count']),
                                    f"{sale['avg_price']:.2f} €"
                                ])
                            
                            # Create table
                            table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 12),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                            elements.append(table)
                            
                        elif rapport.type == 'occupation':
                            # Occupancy report content
                            data = [['Circuit', 'Places Totales', 'Places Réservées', 'Taux Occupation']]
                            for occ in rapport.donnees['occupancy_by_circuit']:
                                data.append([
                                    occ['circuit__titre'],
                                    str(occ['total_places']),
                                    str(occ['total_reserved']),
                                    f"{occ['occupancy_rate']:.1f}%"
                                ])
                            
                            # Create table
                            table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 12),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                            elements.append(table)
                            
                        elif rapport.type == 'clients':
                            # Client report content
                            data = [['Client', 'Total Dépensé', 'Nombre Réservations', 'Moyenne']]
                            for client in rapport.donnees['client_stats']:
                                data.append([
                                    client['client__username'],
                                    f"{client['total_spent']:.2f} €",
                                    str(client['reservation_count']),
                                    f"{client['avg_spent']:.2f} €"
                                ])
                            
                            # Create table
                            table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 12),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                            elements.append(table)
                        
                        # Build the PDF
                        doc.build(elements)
                        
                        # Get the value of the BytesIO buffer
                        pdf = buffer.getvalue()
                        buffer.close()
                        
                        # Create the HTTP response with proper headers
                        response = HttpResponse(content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="rapport_{rapport.type}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
                        response['Content-Length'] = len(pdf)
                        response.write(pdf)
                        
                        return response
                        
                    except Exception as e:
                        error_message = f"Erreur lors de la génération du PDF: {str(e)}"
                        return HttpResponse(error_message, status=500)
                
                messages.success(request, 'Rapport généré avec succès.')
                return redirect('catalogue:sub_admin_report_detail', pk=rapport.pk)
                
            except Exception as e:
                messages.error(request, f"Erreur lors de la génération du rapport: {str(e)}")
                return redirect('catalogue:sub_admin_reports')
    else:
        form = RapportForm()
    
    context = {
        'form': form,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'total_sales': total_sales,
        'total_reservations': total_reservations,
        'overall_occupancy_rate': overall_occupancy_rate,
        'sales_by_circuit': sales_by_circuit,
        'monthly_sales': monthly_sales,
        'occupancy_by_circuit': occupancy_by_circuit,
        'client_stats': client_stats,
    }
    
    return render(request, 'catalogue/sub_admin/reports.html', context)

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_report_detail(request, pk):
    rapport = get_object_or_404(Rapport, pk=pk, cree_par=request.user)
    return render(request, 'catalogue/sub_admin/report_detail.html', {
        'rapport': rapport
    })

@login_required
@user_passes_test(is_sub_admin)
def sub_admin_report_export(request, pk):
    """Export a report as PDF using xhtml2pdf."""
    if not request.user.is_sub_admin:
        raise PermissionDenied("Vous n'avez pas les droits nécessaires pour accéder à cette page.")
    
    rapport = get_object_or_404(Rapport, pk=pk)
    
    # Convert JSON data back to Python objects if needed
    if isinstance(rapport.donnees, str):
        rapport.donnees = json.loads(rapport.donnees)
    
    # Render the template
    html_string = render_to_string('catalogue/sub_admin/report_pdf.html', {
        'rapport': rapport,
        'date_export': timezone.now(),
    })
    
    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(
        html_string,
        dest=buffer,
        encoding='utf-8'
    )
    
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_{rapport.type}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    response.write(pdf)
    
    return response

# Helper functions for report generation
def generer_rapport_ventes(date_debut, date_fin):
    reservations = Reservation.objects.filter(
        date_reservation__range=[date_debut, date_fin],
        statut='confirmee'
    )
    
    total_ventes = reservations.aggregate(
        total=Sum('prix_total'),
        nombre=Count('id')
    )
    
    ventes_par_circuit = reservations.values(
        'circuit__titre'
    ).annotate(
        total=Sum('prix_total'),
        nombre=Count('id')
    )
    
    return {
        'total_ventes': total_ventes['total'] or 0,
        'nombre_reservations': total_ventes['nombre'],
        'ventes_par_circuit': list(ventes_par_circuit)
    }

def generer_rapport_occupation(date_debut, date_fin):
    availabilities = CircuitAvailability.objects.filter(
        date__range=[date_debut, date_fin]
    )
    
    taux_occupation = availabilities.aggregate(
        total_places=Sum('places_disponibles'),
        total_reservees=Sum('places_reservees')
    )
    
    occupation_par_circuit = availabilities.values(
        'circuit__titre'
    ).annotate(
        total_places=Sum('places_disponibles'),
        total_reservees=Sum('places_reservees')
    )
    
    return {
        'taux_occupation_global': (
            (taux_occupation['total_reservees'] or 0) / 
            (taux_occupation['total_places'] or 1) * 100
        ),
        'occupation_par_circuit': list(occupation_par_circuit)
    }

def generer_rapport_clients(date_debut, date_fin):
    clients = User.objects.filter(
        reservations__date_reservation__range=[date_debut, date_fin]
    ).distinct()
    
    stats_clients = clients.annotate(
        nombre_reservations=Count('reservations'),
        montant_total=Sum('reservations__prix_total')
    )
    
    return {
        'nombre_clients': clients.count(),
        'stats_clients': list(stats_clients.values(
            'username', 'email', 'nombre_reservations', 'montant_total'
        ))
    }

def generer_rapport_circuits(date_debut, date_fin):
    circuits = Circuit.objects.filter(
        reservations__date_reservation__range=[date_debut, date_fin]
    ).distinct()
    
    stats_circuits = circuits.annotate(
        nombre_reservations=Count('reservations'),
        montant_total=Sum('reservations__prix_total'),
        taux_occupation=Avg(
            Cast('availabilities__places_reservees', FloatField()) /
            Cast('availabilities__places_disponibles', FloatField()) * 100
        )
    )
    
    return {
        'nombre_circuits': circuits.count(),
        'stats_circuits': list(stats_circuits.values(
            'titre', 'nombre_reservations', 'montant_total', 'taux_occupation'
        ))
    }

# Settings View
@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_settings(request):
    if request.method == 'POST':
        # Handle settings update
        messages.success(request, 'Paramètres mis à jour avec succès.')
        return redirect('sub_admin_settings')
    
    return render(request, 'catalogue/sub_admin/settings.html')

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_reservation_list(request):
    # Get filter parameters
    status = request.GET.get('status')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    sort_by = request.GET.get('sort_by', '-date_reservation')
    export_format = request.GET.get('export')
    payment_status = request.GET.get('payment_status')
    
    # Base queryset with optimizations - force a fresh query
    reservations = Reservation.objects.select_related(
        'circuit', 'client'
    ).prefetch_related(
        'paiements', 'reservation_options', 'reservation_options__option'
    ).all().order_by('-date_reservation')  # Default ordering
    
    # Apply filters
    if status:
        reservations = reservations.filter(statut=status)
    
    if search:
        reservations = reservations.filter(
            Q(circuit__titre__icontains=search) |
            Q(client__username__icontains=search) |
            Q(client__email__icontains=search) |
            Q(client__first_name__icontains=search) |
            Q(client__last_name__icontains=search) |
            Q(id__icontains=search)
        )
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            reservations = reservations.filter(date_reservation__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            reservations = reservations.filter(date_reservation__date__lte=date_to)
        except ValueError:
            pass
    
    # Force evaluation of the queryset to get fresh data
    reservations = list(reservations)
    
    # Calculate payment statistics for each reservation
    for reservation in reservations:
        total_paid = sum(p.montant for p in reservation.paiements.all() if p.statut == 'complete')
        reservation.total_paid = total_paid
        reservation.payment_percentage = (total_paid / reservation.prix_total * 100) if reservation.prix_total > 0 else 0
        reservation.remaining_amount = reservation.prix_total - total_paid
        
        # Add options information
        reservation.options_count = reservation.reservation_options.count()
        reservation.options_total = sum(opt.option.prix * opt.quantite for opt in reservation.reservation_options.all())
        
        # Add payment status
        if reservation.payment_percentage == 100:
            reservation.payment_status = 'complete'
        elif reservation.payment_percentage > 0:
            reservation.payment_status = 'partial'
        else:
            reservation.payment_status = 'pending'
    
    # Apply payment status filter
    if payment_status:
        reservations = [r for r in reservations if r.payment_status == payment_status]
    
    # Get counts for statistics - use the filtered list
    total_count = len(reservations)
    confirmed_count = sum(1 for r in reservations if r.statut == 'confirmee')
    pending_count = sum(1 for r in reservations if r.statut == 'en_attente')
    cancelled_count = sum(1 for r in reservations if r.statut == 'annulee')
    
    # Calculate confirmation rate
    confirmation_rate = (confirmed_count / total_count * 100) if total_count > 0 else 0
    
    # Calculate financial statistics
    total_revenue = sum(r.prix_total for r in reservations if r.statut == 'confirmee')
    total_pending_payments = sum(r.prix_total for r in reservations if r.statut == 'en_attente')
    
    # Calculate monthly statistics
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_revenue = sum(
        r.prix_total for r in reservations 
        if r.statut == 'confirmee' and 
        r.date_reservation.month == current_month and 
        r.date_reservation.year == current_year
    )
    
    monthly_reservations = sum(
        1 for r in reservations 
        if r.date_reservation.month == current_month and 
        r.date_reservation.year == current_year
    )
    
    # Apply sorting
    if sort_by:
        if sort_by.startswith('-'):
            reverse = True
            sort_by = sort_by[1:]
        else:
            reverse = False
        
        if sort_by == 'date_reservation':
            reservations.sort(key=lambda x: x.date_reservation, reverse=reverse)
        elif sort_by == 'prix_total':
            reservations.sort(key=lambda x: x.prix_total, reverse=reverse)
        elif sort_by == 'id':
            reservations.sort(key=lambda x: x.id, reverse=reverse)
    
    # Get recent activity (last 5 reservations)
    recent_activity = reservations[:5]
    
    # Get upcoming reservations (next 7 days)
    upcoming_reservations = [
        r for r in reservations 
        if r.date_reservation >= timezone.now() and 
        r.date_reservation <= timezone.now() + timezone.timedelta(days=7)
    ][:5]
    
    # Handle export
    if export_format:
        if export_format == 'excel':
            return export_reservations_excel(reservations)
        elif export_format == 'pdf':
            return export_reservations_pdf(reservations)
        elif export_format == 'csv':
            return export_reservations_csv(reservations)
    
    context = {
        'reservations': reservations,
        'recent_activity': recent_activity,
        'upcoming_reservations': upcoming_reservations,
        'status': status,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'payment_status': payment_status,
        'reservation_status_choices': Reservation.STATUT_CHOICES,
        'total_count': total_count,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
        'total_revenue': total_revenue,
        'total_pending_payments': total_pending_payments,
        'monthly_revenue': monthly_revenue,
        'monthly_reservations': monthly_reservations,
        'confirmation_rate': confirmation_rate,
        'current_date': timezone.now(),
        'current_month': current_month,
        'current_year': current_year,
    }
    return render(request, 'catalogue/sub_admin/reservation_list.html', context)

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_reservation_print(request, pk):
    """View for printing a single reservation"""
    reservation = get_object_or_404(Reservation.objects.select_related(
        'circuit', 'client'
    ).prefetch_related(
        'paiements', 'reservation_options', 'reservation_options__option'
    ), pk=pk)
    
    # Calculate payment statistics
    total_paid = sum(p.montant for p in reservation.paiements.all() if p.statut == 'complete')
    payment_percentage = (total_paid / reservation.prix_total * 100) if reservation.prix_total > 0 else 0
    remaining_amount = reservation.prix_total - total_paid
    
    # Calculate options total
    options_total = sum(opt.option.prix * opt.quantite for opt in reservation.reservation_options.all())
    
    context = {
        'reservation': reservation,
        'total_paid': total_paid,
        'payment_percentage': payment_percentage,
        'remaining_amount': remaining_amount,
        'options_total': options_total,
        'print_only': True,  # Flag to indicate this is for printing
    }
    return render(request, 'catalogue/sub_admin/reservation_print.html', context)

def export_reservations_excel(reservations):
    """Export reservations to Excel format"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4CAF50',
        'font_color': 'white',
        'border': 1
    })
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'left'
    })
    date_format = workbook.add_format({
        'border': 1,
        'num_format': 'dd/mm/yyyy'
    })
    currency_format = workbook.add_format({
        'border': 1,
        'num_format': '#,##0.00 €'
    })

    # Write headers
    headers = [
        'ID', 'Client', 'Circuit', 'Date Réservation', 'Date Départ',
        'Nombre Voyageurs', 'Statut', 'Prix Total', 'Montant Payé',
        'Montant Restant', 'Options'
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Write data
    for row, reservation in enumerate(reservations, start=1):
        total_paid = sum(p.montant for p in reservation.paiements.all() if p.statut == 'complete')
        remaining_amount = reservation.prix_total - total_paid
        options = ', '.join(f"{opt.option.nom} (x{opt.quantite})" for opt in reservation.reservation_options.all())

        worksheet.write(row, 0, reservation.id, cell_format)
        worksheet.write(row, 1, str(reservation.client), cell_format)
        worksheet.write(row, 2, reservation.circuit.titre, cell_format)
        worksheet.write(row, 3, reservation.date_reservation, date_format)
        worksheet.write(row, 4, reservation.date_depart, date_format)
        worksheet.write(row, 5, reservation.nombre_voyageurs, cell_format)
        worksheet.write(row, 6, reservation.get_statut_display(), cell_format)
        worksheet.write(row, 7, float(reservation.prix_total), currency_format)
        worksheet.write(row, 8, float(total_paid), currency_format)
        worksheet.write(row, 9, float(remaining_amount), currency_format)
        worksheet.write(row, 10, options, cell_format)

    # Adjust column widths
    for col in range(len(headers)):
        worksheet.set_column(col, col, 15)

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response

def export_reservations_pdf(reservations):
    """Export reservations to PDF format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    elements.append(Paragraph(f"Liste des Réservations - {datetime.now().strftime('%d/%m/%Y')}", title_style))
    elements.append(Spacer(1, 20))

    # Prepare table data
    data = [['ID', 'Client', 'Circuit', 'Date', 'Statut', 'Prix Total', 'Payé', 'Restant']]
    
    for reservation in reservations:
        total_paid = sum(p.montant for p in reservation.paiements.all() if p.statut == 'complete')
        remaining_amount = reservation.prix_total - total_paid
        
        row = [
            str(reservation.id),
            str(reservation.client),
            reservation.circuit.titre,
            reservation.date_reservation.strftime('%d/%m/%Y'),
            reservation.get_statut_display(),
            f"{reservation.prix_total:.2f} €",
            f"{total_paid:.2f} €",
            f"{remaining_amount:.2f} €"
        ]
        data.append(row)

    # Create table
    table = Table(data, colWidths=[1*inch, 2*inch, 2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return response

def export_reservations_csv(reservations):
    """Export reservations to CSV format"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=reservations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Client', 'Circuit', 'Date Réservation', 'Date Départ',
        'Nombre Voyageurs', 'Statut', 'Prix Total', 'Montant Payé',
        'Montant Restant', 'Options'
    ])

    for reservation in reservations:
        total_paid = sum(p.montant for p in reservation.paiements.all() if p.statut == 'complete')
        remaining_amount = reservation.prix_total - total_paid
        options = ', '.join(f"{opt.option.nom} (x{opt.quantite})" for opt in reservation.reservation_options.all())

        writer.writerow([
            reservation.id,
            str(reservation.client),
            reservation.circuit.titre,
            reservation.date_reservation.strftime('%d/%m/%Y'),
            reservation.date_depart.strftime('%d/%m/%Y'),
            reservation.nombre_voyageurs,
            reservation.get_statut_display(),
            f"{reservation.prix_total:.2f}",
            f"{total_paid:.2f}",
            f"{remaining_amount:.2f}",
            options
        ])

    return response

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation.objects.select_related(
        'circuit', 'client'
    ), pk=pk)
    paiements = reservation.paiements.all().order_by('-date_paiement')
    
    # Calculate payment statistics
    total_paid = paiements.filter(statut='complete').aggregate(
        total=Sum('montant')
    )['total'] or 0
    remaining_amount = reservation.prix_total - total_paid
    
    context = {
        'reservation': reservation,
        'paiements': paiements,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
        'payment_percentage': (total_paid / reservation.prix_total * 100) if reservation.prix_total > 0 else 0
    }
    return render(request, 'catalogue/sub_admin/reservation_detail.html', context)

@login_required
@user_passes_test(is_admin_or_sub_admin)
def sub_admin_reservation_update(request, pk):
    reservation = get_object_or_404(Reservation.objects.select_related(
        'circuit', 'client'
    ), pk=pk)
    
    if request.method == 'POST':
        statut = request.POST.get('statut')
        if statut in dict(Reservation.STATUT_CHOICES):
            old_status = reservation.statut
            reservation.statut = statut
            reservation.save()
            
            # Update circuit availability if needed
            if old_status != statut:
                if statut == 'confirmee':
                    # Decrease available places
                    circuit = reservation.circuit
                    circuit.places_disponibles -= reservation.nombre_voyageurs
                    circuit.save()
                elif old_status == 'confirmee' and statut in ['en_attente', 'annulee']:
                    # Increase available places
                    circuit = reservation.circuit
                    circuit.places_disponibles += reservation.nombre_voyageurs
                    circuit.save()
            
            messages.success(request, 'Statut de la réservation mis à jour avec succès.')
            return redirect('sub_admin_reservation_detail', pk=reservation.pk)
        else:
            messages.error(request, 'Statut invalide.')
    
    context = {
        'reservation': reservation,
        'reservation_status_choices': Reservation.STATUT_CHOICES
    }
    return render(request, 'catalogue/sub_admin/reservation_update.html', context)

@login_required
@require_POST
def validate_reservation(request, pk):
    """View to validate a reservation"""
    if not request.user.is_sub_admin:
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'avez pas les permissions nécessaires'
        }, status=403)
    
    try:
        with transaction.atomic():  # Use transaction to ensure data consistency
            reservation = get_object_or_404(Reservation.objects.select_related('circuit'), pk=pk)
            
            # Check if reservation can be validated
            if reservation.statut != 'en_attente':
                return JsonResponse({
                    'success': False,
                    'message': 'Cette réservation ne peut pas être validée'
                }, status=400)
            
            # Check if there are enough places available
            if reservation.circuit.places_disponibles < reservation.nombre_voyageurs:
                return JsonResponse({
                    'success': False,
                    'message': 'Pas assez de places disponibles pour valider cette réservation'
                }, status=400)
            
            # Update circuit availability
            circuit = reservation.circuit
            circuit.places_disponibles -= reservation.nombre_voyageurs
            circuit.save()
            
            # Update reservation status
            reservation.statut = 'confirmee'
            reservation.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Réservation validée avec succès'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Une erreur est survenue: {str(e)}'
        }, status=500)

@login_required
@require_POST
def cancel_reservation(request, pk):
    """View to cancel a reservation"""
    if not request.user.is_sub_admin:
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'avez pas les permissions nécessaires'
        }, status=403)
    
    try:
        with transaction.atomic():  # Use transaction to ensure data consistency
            reservation = get_object_or_404(Reservation.objects.select_related('circuit'), pk=pk)
            
            # Check if reservation can be cancelled
            if reservation.statut == 'annulee':
                return JsonResponse({
                    'success': False,
                    'message': 'Cette réservation est déjà annulée'
                }, status=400)
            
            # If the reservation was confirmed, update circuit availability
            if reservation.statut == 'confirmee':
                circuit = reservation.circuit
                circuit.places_disponibles += reservation.nombre_voyageurs
                circuit.save()
            
            # Update reservation status
            reservation.statut = 'annulee'
            reservation.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Réservation annulée avec succès'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Une erreur est survenue: {str(e)}'
        }, status=500)

@login_required
@user_passes_test(is_admin_or_sub_admin)  # Add permission check
def delete_reservation(request, pk):
    try:
        with transaction.atomic():  # Use transaction to ensure data consistency
            reservation = get_object_or_404(Reservation.objects.select_related('circuit'), pk=pk)
            
            # Only allow deletion of cancelled reservations
            if reservation.statut != 'annulee':
                messages.error(request, "Seules les réservations annulées peuvent être supprimées.")
                return redirect('sub_admin_reservation_list')
            
            if request.method == 'POST':
                # Delete related data first
                reservation.paiements.all().delete()  # Delete all payments
                reservation.reservation_options.all().delete()  # Delete all options
                reservation.delete()  # Delete the reservation itself
                
                messages.success(request, "La réservation a été supprimée avec succès.")
                return redirect('sub_admin_reservation_list')
            
            return render(request, 'catalogue/sub_admin/reservation_confirm_delete.html', {
                'reservation': reservation
            })
            
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression: {str(e)}")
        return redirect('sub_admin_reservation_list')

@login_required
def user_chat(request):
    """View for users to chat with sub-admins."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get all sub-admins
    sub_admins = User.objects.filter(groups__name='SubAdmin', is_active=True)
    
    context = {
        'sub_admins': sub_admins,
    }
    return render(request, 'catalogue/user/chat.html', context)

@login_required
def user_chat_messages(request):
    """Get messages for the user's chat with sub-admins."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=401)
    
    try:
        # Get all messages between the user and any sub-admin
        messages = Communication.objects.filter(
            Q(expediteur=request.user) | Q(destinataire=request.user)
        ).order_by('date_creation')
        
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                'id': message.id,
                'content': message.message,
                'time': message.date_creation.strftime('%H:%M'),
                'date': message.date_creation.isoformat(),
                'is_sent': message.expediteur == request.user,
                'status': 'read' if message.lu else 'sent'
            })
        
        return JsonResponse({
            'success': True,
            'messages': formatted_messages
        })
    except Exception as e:
        logger.error(f"Error loading user chat messages: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors du chargement des messages'
        }, status=500)

@login_required
def user_send_message(request):
    """Handle sending messages from users to sub-admins."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    
    try:
        # Log the raw request body for debugging
        logger.debug(f"Raw request body: {request.body}")
        
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({
                'success': False,
                'message': 'Le message ne peut pas être vide'
            }, status=400)
        
        if len(message) > 1000:
            return JsonResponse({
                'success': False,
                'message': 'Le message ne peut pas dépasser 1000 caractères'
            }, status=400)
        
        # Get all active sub-admins (check both group and role)
        sub_admins = User.objects.filter(
            Q(groups__name='SubAdmin') | Q(role='sub_admin'),
            is_active=True
        ).distinct()
        
        logger.debug(f"Found {sub_admins.count()} active sub-admins")
        
        if not sub_admins.exists():
            # If no sub-admins are available, create a system message
            system_user = User.objects.filter(is_superuser=True).first()
            if not system_user:
                raise Exception("Aucun administrateur système disponible")
                
            with transaction.atomic():
                communication = Communication.objects.create(
                    expediteur=request.user,
                    destinataire=system_user,
                    message=f"[Message en attente] {message}",
                    lu=False,
                    date_envoi=None,
                    statut='pending'
                )
                logger.debug(f"Created pending communication record: {communication.id}")
                
                formatted_message = {
                    'id': communication.id,
                    'content': communication.message,
                    'time': communication.date_creation.strftime('%H:%M'),
                    'date': communication.date_creation.isoformat(),
                    'is_sent': True,
                    'status': 'pending'
                }
                
                return JsonResponse({
                    'success': True,
                    'message': formatted_message
                })
        
        # If we have sub-admins, send the message to all of them
        communications = []
        notifications = []
        
        with transaction.atomic():
            for sub_admin in sub_admins:
                # Create communication record for each sub-admin
                communication = Communication.objects.create(
                    expediteur=request.user,
                    destinataire=sub_admin,
                    message=message,
                    lu=False,
                    date_envoi=timezone.now(),
                    statut='envoye'
                )
                communications.append(communication)
                logger.debug(f"Created communication record for sub-admin {sub_admin.id}: {communication.id}")
                
                # Create notification for each sub-admin
                notification = Notification.objects.create(
                    destinataire=sub_admin,
                    type='systeme',
                    titre='Nouveau message',
                    message=f"Nouveau message de {request.user.get_full_name() or request.user.username}",
                    lien=f"/sub-admin/communication/?user_id={request.user.id}",
                    priorite='normale'
                )
                notifications.append(notification)
                logger.debug(f"Created notification for sub-admin {sub_admin.id}: {notification.id}")
            
            # Use the first communication for the response
            first_communication = communications[0]
            formatted_message = {
                'id': first_communication.id,
                'content': first_communication.message,
                'time': first_communication.date_creation.strftime('%H:%M'),
                'date': first_communication.date_creation.isoformat(),
                'is_sent': True,
                'status': 'sent'
            }
            
            return JsonResponse({
                'success': True,
                'message': formatted_message
            })
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Format de données invalide'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in user_send_message: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'envoi du message: {str(e)}'
        }, status=500)
