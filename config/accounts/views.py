from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import User
from users.models import UserProfile
from .forms import UserRegistrationForm

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': request.user.userprofile
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        profile = user.userprofile
        profile.telephone = request.POST.get('telephone', '')
        profile.adresse = request.POST.get('adresse', '')
        profile.save()
        
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('profile')
    
    return render(request, 'accounts/profile_edit.html', {
        'user': request.user,
        'profile': request.user.userprofile
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            messages.success(request, 'Compte créé avec succès!')
            return redirect('catalogue')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login') 