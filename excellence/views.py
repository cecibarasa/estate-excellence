from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.shortcuts import get_object_or_404

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about-us.html')

def properties(request):
    estates = Estate.objects.all()
    return render(request, 'properties.html', {'estates': estates})

def upload_property(request):
    if request.method == 'POST':
        form = EstateForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.save()
            return redirect('properties')
    else:
        form = EstateForm()
    return render(request, 'upload_property.html', locals())

def contact(request):
    return render(request, 'contact-us.html')

def estate_detail(request, pk):
    estate = get_object_or_404(Estate, pk=pk)
    return render(request, 'estate_detail.html', {'estate': estate})