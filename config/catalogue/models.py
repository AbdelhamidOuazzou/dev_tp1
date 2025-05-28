from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class Destination(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)
    prix_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nom

class Circuit(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='circuits')
    titre = models.CharField(max_length=100)
    description = models.TextField()
    duree = models.IntegerField(help_text="Durée en jours")
    prix_base = models.DecimalField(max_digits=10, decimal_places=2)
    date_depart = models.DateField()
    places_disponibles = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.titre} - {self.destination.nom}"

class OptionSupplement(models.Model):
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='options')
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nom} - {self.circuit.titre}"

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('terminee', 'Terminée'),
    ]

    circuit = models.ForeignKey(Circuit, on_delete=models.PROTECT, related_name='reservations')
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_depart = models.DateField()
    nombre_voyageurs = models.IntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.ManyToManyField(OptionSupplement, through='ReservationOption')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Réservation {self.id} - {self.circuit.titre}"

    def calculer_prix_total(self):
        prix_base = self.circuit.prix_base * self.nombre_voyageurs
        prix_options = sum(opt.prix * opt.quantite for opt in self.reservation_options.all())
        return prix_base + prix_options

    def save(self, *args, **kwargs):
        if not self.prix_total:
            self.prix_total = self.calculer_prix_total()
        super().save(*args, **kwargs)

class ReservationOption(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='reservation_options')
    option = models.ForeignKey(OptionSupplement, on_delete=models.PROTECT)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.option.nom} x{self.quantite}"

    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = self.option.prix
        super().save(*args, **kwargs)

class Paiement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('complete', 'Complété'),
        ('annule', 'Annulé'),
        ('rembourse', 'Remboursé'),
    ]

    TYPE_CHOICES = [
        ('acompte', 'Acompte'),
        ('solde', 'Solde'),
        ('remboursement', 'Remboursement'),
    ]

    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_paiement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_paiement = models.DateTimeField(auto_now_add=True)
    numero_facture = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Paiement {self.numero_facture} - {self.reservation}"

    def save(self, *args, **kwargs):
        if not self.numero_facture:
            # Générer un numéro de facture unique
            import datetime
            prefix = datetime.datetime.now().strftime('%Y%m%d')
            last_payment = Paiement.objects.filter(numero_facture__startswith=prefix).order_by('-numero_facture').first()
            if last_payment:
                last_number = int(last_payment.numero_facture[-4:])
                new_number = str(last_number + 1).zfill(4)
            else:
                new_number = '0001'
            self.numero_facture = f"{prefix}-{new_number}"
        super().save(*args, **kwargs)

class CircuitAvailability(models.Model):
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    places_disponibles = models.IntegerField(validators=[MinValueValidator(0)])
    places_reservees = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=[
        ('disponible', 'Disponible'),
        ('complet', 'Complet'),
        ('ferme', 'Fermé'),
    ], default='disponible')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['circuit', 'date']
        ordering = ['date']

    def __str__(self):
        return f"{self.circuit.titre} - {self.date}"

    def places_restantes(self):
        return self.places_disponibles - self.places_reservees

class Communication(models.Model):
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('notification', 'Notification'),
        ('message', 'Message direct'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('envoye', 'Envoyé'),
        ('echoue', 'Échoué'),
    ]

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='communications', null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communications_recues')
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communications_envoyees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    lu = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Communication'
        verbose_name_plural = 'Communications'
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.sujet}"

class Rapport(models.Model):
    TYPE_CHOICES = [
        ('ventes', 'Rapport des Ventes'),
        ('occupation', 'Taux d\'Occupation'),
        ('clients', 'Analyse des Clients'),
        ('circuits', 'Performance des Circuits'),
    ]

    PERIODE_CHOICES = [
        ('jour', 'Journalier'),
        ('semaine', 'Hebdomadaire'),
        ('mois', 'Mensuel'),
        ('annee', 'Annuel'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    periode = models.CharField(max_length=20, choices=PERIODE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    donnees = models.JSONField()  # Stockage des données du rapport
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rapports_crees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.get_type_display()} - {self.date_debut} au {self.date_fin}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('reservation', 'Réservation'),
        ('paiement', 'Paiement'),
        ('disponibilite', 'Disponibilité'),
        ('systeme', 'Système'),
    ]

    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    lien = models.CharField(max_length=200, blank=True)  # URL optionnelle pour redirection

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.destinataire.username}"
