from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.catalogue, name='catalogue'),
    path('circuit/<int:id>/', views.circuit_detail, name='circuit_detail'),
    
    # Reservation URLs
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('circuit/<int:circuit_id>/reserver/', views.reserver_circuit, name='reserver_circuit'),
    path('reservations/<int:reservation_id>/paiement/', views.paiement_create, name='paiement_create'),
    path('paiements/<int:paiement_id>/simuler/', views.paiement_simuler, name='paiement_simuler'),
    
    # Agent URLs
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/reservations/', views.agent_reservation_list, name='agent_reservation_list'),
    path('agent/reservations/<int:pk>/', views.agent_reservation_detail, name='agent_reservation_detail'),
    path('agent/reservations/<int:pk>/update/', views.agent_reservation_update, name='agent_reservation_update'),
    path('agent/payments/', views.payment_management, name='payment_management'),
    path('agent/payments/simuler/', views.paiement_simuler, name='paiement_simuler'),
    path('agent/payments/<int:pk>/', views.paiement_detail, name='agent_payment_detail'),
    path('agent/payments/<int:pk>/edit/', views.paiement_edit, name='agent_payment_edit'),
    path('agent/payments/<int:pk>/delete/', views.paiement_delete, name='agent_payment_delete'),
    
    # Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Destination URLs
    path('admin/destinations/', views.destination_list, name='admin_destination_list'),
    path('admin/destinations/create/', views.destination_create, name='admin_destination_create'),
    path('admin/destinations/<int:pk>/edit/', views.destination_edit, name='admin_destination_edit'),
    path('admin/destinations/<int:pk>/delete/', views.destination_delete, name='admin_destination_delete'),
    
    # Circuit URLs
    path('admin/circuits/', views.circuit_list, name='admin_circuit_list'),
    path('admin/circuits/create/', views.circuit_create, name='admin_circuit_create'),
    path('admin/circuits/<int:pk>/edit/', views.circuit_edit, name='admin_circuit_edit'),
    path('admin/circuits/<int:pk>/delete/', views.circuit_delete, name='admin_circuit_delete'),
    
    # Option URLs
    path('admin/options/', views.option_list, name='admin_option_list'),
    path('admin/options/create/', views.option_create, name='admin_option_create'),
    path('admin/options/<int:pk>/edit/', views.option_edit, name='admin_option_edit'),
    path('admin/options/<int:pk>/delete/', views.option_delete, name='admin_option_delete'),

    # Admin Reservation URLs
    path('admin/reservations/', views.admin_reservation_list, name='admin_reservation_list'),
    path('admin/reservations/<int:pk>/', views.admin_reservation_detail, name='admin_reservation_detail'),
    path('admin/reservations/<int:pk>/update/', views.admin_reservation_update, name='admin_reservation_update'),

    # Sub-admin URLs
    path('sub-admin/dashboard/', views.sub_admin_dashboard, name='sub_admin_dashboard'),
    
    # Sub-admin Availability URLs
    path('sub-admin/availability/', views.sub_admin_availability, name='sub_admin_availability'),
    path('sub-admin/availability/<int:pk>/delete/', views.sub_admin_availability_delete, name='sub_admin_availability_delete'),
    
    # Sub-admin Reservation URLs
    path('sub-admin/reservations/', views.sub_admin_reservation_list, name='sub_admin_reservation_list'),
    path('sub-admin/reservations/<int:pk>/', views.sub_admin_reservation_detail, name='sub_admin_reservation_detail'),
    path('sub-admin/reservations/<int:pk>/update/', views.sub_admin_reservation_update, name='sub_admin_reservation_update'),
    path('sub-admin/reservations/<int:reservation_id>/paiement/', views.paiement_create, name='sub_admin_paiement_create'),
    path('sub-admin/reservations/<int:pk>/print/', views.sub_admin_reservation_print, name='sub_admin_reservation_print'),
    path('sub-admin/reservations/<int:pk>/delete/', views.delete_reservation, name='sub_admin_reservation_delete'),
    
    # Sub-admin Communication URLs
    path('sub-admin/communication/', views.sub_admin_communication, name='sub_admin_communication'),
    path('sub-admin/communication/messages/<int:user_id>/', views.get_user_messages, name='get_user_messages'),
    path('sub-admin/communication/mark-read/<int:user_id>/', views.mark_messages_read, name='mark_messages_read'),
    path('sub-admin/communication/typing/<int:user_id>/', views.send_typing_status, name='send_typing_status'),
    
    # Sub-admin Reports URLs
    path('sub-admin/reports/', views.sub_admin_reports, name='sub_admin_reports'),
    path('sub-admin/reports/<int:pk>/', views.sub_admin_report_detail, name='sub_admin_report_detail'),
    path('sub-admin/reports/<int:pk>/export/', views.sub_admin_report_export, name='sub_admin_report_export'),
    
    # Sub-admin Settings URL
    path('sub-admin/settings/', views.sub_admin_settings, name='sub_admin_settings'),
    
    # Sub-admin Destination URLs
    path('sub-admin/destinations/', views.sub_admin_destination_list, name='sub_admin_destination_list'),
    path('sub-admin/destinations/create/', views.sub_admin_destination_create, name='sub_admin_destination_create'),
    path('sub-admin/destinations/<int:pk>/edit/', views.sub_admin_destination_edit, name='sub_admin_destination_edit'),
    path('sub-admin/destinations/<int:pk>/delete/', views.sub_admin_destination_delete, name='sub_admin_destination_delete'),
    
    # Sub-admin Circuit URLs
    path('sub-admin/circuits/', views.sub_admin_circuit_list, name='sub_admin_circuit_list'),
    path('sub-admin/circuits/create/', views.sub_admin_circuit_create, name='sub_admin_circuit_create'),
    path('sub-admin/circuits/<int:pk>/edit/', views.sub_admin_circuit_edit, name='sub_admin_circuit_edit'),
    path('sub-admin/circuits/<int:pk>/delete/', views.sub_admin_circuit_delete, name='sub_admin_circuit_delete'),
    
    # Sub-admin Option URLs
    path('sub-admin/options/', views.sub_admin_option_list, name='sub_admin_option_list'),
    path('sub-admin/options/create/', views.sub_admin_option_create, name='sub_admin_option_create'),
    path('sub-admin/options/<int:pk>/edit/', views.sub_admin_option_edit, name='sub_admin_option_edit'),
    path('sub-admin/options/<int:pk>/delete/', views.sub_admin_option_delete, name='sub_admin_option_delete'),

    path('dashboard/', views.dashboard, name='dashboard'),

    # Reservation management URLs
    path('sub-admin/reservations/<int:pk>/validate/', 
         views.validate_reservation, 
         name='sub_admin_reservation_validate'),
    path('sub-admin/reservations/<int:pk>/cancel/', 
         views.cancel_reservation, 
         name='sub_admin_reservation_cancel'),

    # User chat URLs
    path('user/chat/', views.user_chat, name='user_chat'),
    path('user/chat/messages/', views.user_chat_messages, name='user_chat_messages'),
    path('user/chat/send/', views.user_send_message, name='user_send_message'),
]
