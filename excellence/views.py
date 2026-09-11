from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_user_model, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator


# Create your views here.

def register(request):
    AuthUser = get_user_model()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'hide_navbar': True, 'hide_footer': True, 'form': form})

def login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('index')

        error_message = "Invalid username or password."
        return render(
            request,
            'registration/login.html',
            {'error_message': error_message, 'hide_navbar': True, 'hide_footer': True, 'form': form}
        )

    return render(request, 'registration/login.html', {'hide_navbar': True, 'hide_footer': True, 'form': form})

@login_required
def profile(request):
    return render(request, 'registration/profile.html')

@login_required
def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    return redirect('index')

@login_required
def index(request):
    estates = Estate.objects.all().order_by('-pk')
    location = request.GET.get('location')
    property_type = request.GET.get('property_type')
    price_range = request.GET.get('price_range')

    if location:
        estates = estates.filter(location_name__icontains=location)

    if property_type:
        estates = estates.filter(name__icontains=property_type)

    if price_range:
        if price_range == '1':
            estates = estates.filter(name__icontains='')

    return render(request, 'index.html', {
        'estates': estates,
        'selected_location': location,
        'selected_property_type': property_type,
        'selected_price_range': price_range,
    })

@login_required
def about(request):
    return render(request, 'about-us.html')

def properties(request):
    estates = Estate.objects.all().order_by('-id')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(estates, 3)
    page_obj = paginator.get_page(page_number)

    return render(request, 'properties.html', {'estates': page_obj.object_list, 'page_obj': page_obj, 'paginator': paginator,})

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
    estates = Estate.objects.all()
    
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            # Optional: Link this contact message to the specific estate
            # contact.estate = estate 
            contact.save()
            return redirect('estate_detail', pk=pk)
        # If the form is invalid, we do nothing and let it fall through 
        # to the render() function so Django can display the validation errors.
    else:
        # ✅ Added: This handles the initial page load (GET request)
        form = ContactForm()
    print(estate.exact_address)
    return render(request, 'estate_detail.html', {
        'estate': estate, 
        'form': form, # This is now safely defined for both GET and POST requests!
        'estates': estates
    })


@require_POST
def update_location(request, pk):
    # staff-only endpoint to update an estate's coordinates via AJAX
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden('staff only')

    estate = get_object_or_404(Estate, pk=pk)
    try:
        lat = request.POST.get('latitude') or request.POST.get('lat')
        lng = request.POST.get('longitude') or request.POST.get('lng')
        if lat is None or lng is None:
            return JsonResponse({'ok': False, 'error': 'missing coordinates'}, status=400)
        # store with Decimal where possible
        from decimal import Decimal
        try:
            estate.latitude = Decimal(str(float(lat)))
            estate.longitude = Decimal(str(float(lng)))
        except Exception:
            estate.latitude = float(lat)
            estate.longitude = float(lng)

        estate.update_exact_address_from_coordinates()
        estate.save()
        return JsonResponse({
            'ok': True,
            'latitude': str(estate.latitude),
            'longitude': str(estate.longitude),
            'exact_address': estate.exact_address,
            'display_location': estate.display_location,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@login_required
@ensure_csrf_cookie
def edit_estate(request, pk):
    # staff-only page to edit estate location visually
    if not request.user.is_staff:
        return HttpResponseForbidden('staff only')
    estate = get_object_or_404(Estate, pk=pk)
    if request.method == 'POST':
        form = EstateForm(request.POST, request.FILES, instance=estate)
        if form.is_valid():
            form.save()
            return redirect('estate_detail', pk=pk)
    else:
        form = EstateForm(instance=estate)
    return render(request, 'edit_estate.html', {'form': form, 'estate': estate, 'csrf_token': request.META.get('CSRF_COOKIE', '')})

def footer(request):
    estates = Estate.objects.all()
    return render(request, 'footer.html', {'estates': estates})