from django import forms
from .models import Destination, Circuit, OptionSupplement, Reservation, ReservationOption, Paiement, CircuitAvailability, Communication, Rapport, Notification
from django.utils import timezone

class DestinationForm(forms.ModelForm):
    prix_base = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'step': '0.01',
            'min': '0',
            'required': True
        })
    )

    class Meta:
        model = Destination
        fields = ['nom', 'description', 'image', 'prix_base']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CircuitForm(forms.ModelForm):
    prix_base = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'step': '0.01',
            'min': '0',
            'required': True
        })
    )

    class Meta:
        model = Circuit
        fields = ['destination', 'titre', 'description', 'duree', 'prix_base', 'date_depart', 'places_disponibles']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_depart': forms.DateInput(attrs={'type': 'date'}),
        }

class OptionSupplementForm(forms.ModelForm):
    class Meta:
        model = OptionSupplement
        fields = ['circuit', 'nom', 'description', 'prix']
        widgets = {
            'circuit': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
        }

    def __init__(self, *args, **kwargs):
        self.circuit = kwargs.pop('circuit', None)
        super().__init__(*args, **kwargs)
        if self.circuit:
            self.fields['circuit'].queryset = self.circuit.options.all()

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_depart', 'nombre_voyageurs', 'notes']
        widgets = {
            'date_depart': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'nombre_voyageurs': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            })
        }

    def __init__(self, *args, **kwargs):
        self.circuit = kwargs.pop('circuit', None)
        super().__init__(*args, **kwargs)
        if self.circuit:
            self.fields['date_depart'].initial = self.circuit.date_depart
            self.fields['nombre_voyageurs'].widget.attrs['max'] = self.circuit.places_disponibles

    def clean_nombre_voyageurs(self):
        nombre_voyageurs = self.cleaned_data['nombre_voyageurs']
        if self.circuit and nombre_voyageurs > self.circuit.places_disponibles:
            raise forms.ValidationError(
                f"Il n'y a que {self.circuit.places_disponibles} places disponibles."
            )
        return nombre_voyageurs

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.circuit:
            instance.circuit = self.circuit
        if commit:
            instance.save()
        return instance

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant', 'type_paiement', 'notes']
        widgets = {
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
            }),
            'type_paiement': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ajoutez des notes ou commentaires sur ce paiement',
            }),
        }

    def clean_montant(self):
        montant = self.cleaned_data['montant']
        reservation = self.instance.reservation if self.instance.pk else self.initial.get('reservation')
        
        if reservation:
            total_paid = sum(p.montant for p in reservation.paiements.all() if p.pk != self.instance.pk)
            remaining_amount = reservation.prix_total - total_paid
            
            if montant > remaining_amount:
                raise forms.ValidationError(
                    f"Le montant ne peut pas dépasser le montant restant à payer ({remaining_amount} €)"
                )
        
        return montant

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.date_paiement:
            instance.date_paiement = timezone.now()
        if commit:
            instance.save()
        return instance

class CircuitAvailabilityForm(forms.ModelForm):
    class Meta:
        model = CircuitAvailability
        fields = ['circuit', 'date', 'places_disponibles']
        widgets = {
            'circuit': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'places_disponibles': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order circuits by title
        self.fields['circuit'].queryset = Circuit.objects.all().order_by('titre')

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['type', 'sujet', 'message']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'required': True
            })
        }

class RapportForm(forms.ModelForm):
    class Meta:
        model = Rapport
        fields = ['type', 'periode', 'date_debut', 'date_fin', 'titre', 'description']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'periode': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'date_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")

        return cleaned_data

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['type', 'titre', 'message', 'priorite', 'lien']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True
            }),
            'priorite': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'lien': forms.URLInput(attrs={
                'class': 'form-control'
            })
        } 