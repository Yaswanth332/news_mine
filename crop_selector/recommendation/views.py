# recommendation/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import CropQuery, CropMaster
from .forms import CropQueryForm

def home(request):
    return render(request, 'recommendation/home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'recommendation/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('recommend')
    else:
        form = AuthenticationForm()
    return render(request, 'recommendation/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def recommend_crop(request):
    if request.method == 'POST':
        form = CropQueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.user = request.user
            query.save()

            matched_crops = []
            for crop in CropMaster.objects.all():
                score = 0
                if crop.soil_texture == query.soil_texture:
                    score += 1
                if crop.organic_matter == query.organic_matter:
                    score += 1
                if crop.drainage_status == query.drainage_status:
                    score += 1
                if crop.soil_ph_min <= query.soil_ph <= crop.soil_ph_max:
                    score += 1
                if crop.rainfall_min <= query.rainfall_mm <= crop.rainfall_max:
                    score += 1
                if crop.temperature_min <= query.avg_temperature <= crop.temperature_max:
                    score += 1
                if crop.season == query.season or crop.season == 'any':
                    score += 1
                if crop.previous_crop.lower() == query.previous_crop.lower():
                    score += 1

                matched_crops.append((crop, score))

            matched_crops.sort(key=lambda x: x[1], reverse=True)
            top_crops = [c[0] for c in matched_crops[:10]]

            return render(request, 'recommendation/results.html', {
                'crops': top_crops,
                'form': form,
                'query_id': query.id
            })
    else:
        form = CropQueryForm()
    return render(request, 'recommendation/recommend.html', {'form': form})

@login_required
def recommendation_results(request, query_id):
    query = get_object_or_404(CropQuery, id=query_id, user=request.user)
    return redirect('recommend')

def crop_detail(request, pk):
    crop = get_object_or_404(CropMaster, id=pk)
    return render(request, 'recommendation/crop_detail.html', {'crop': crop})
