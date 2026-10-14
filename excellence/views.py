from django.core.serializers import json
from django.db.migrations import state
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, request
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_user_model, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.conf import settings
from django.core.files.base import ContentFile
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import json
import os
from google_auth_oauthlib.flow import Flow
from unittest.mock import patch, MagicMock
from rest_framework import serializers
from .serializers import ImageSerializer


# Create your views here.

CLIENT_SECRET_FILE = os.path.join(settings.BASE_DIR, 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
REDIRECT_URI = "https://estate-excellence-1.onrender.com/accounts/google/login/callback/"

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
    estates = Estate.objects.all()
    return render(request, 'about-us.html', {'estates': estates})

def properties(request):
    estates = Estate.objects.all().order_by('-id')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(estates, 3)
    page_obj = paginator.get_page(page_number)

    return render(request, 'properties.html', {'estates': page_obj.object_list, 'page_obj': page_obj, 'paginator': paginator,})


def upload_image_from_drive(request, file_id, *args, **kwargs):
    if request.method == "POST":

        data = json.loads(request.body)

        file_id = data.get("file_id")

        return JsonResponse({

        "success": True,

        "file_id": file_id

        })

    return JsonResponse({
    "error": "POST request required"
    }, status=400)

def google_drive_login(request):
    if not os.path.exists(CLIENT_SECRET_FILE):
        return HttpResponse(
            "Google OAuth client secret file is missing. Create client_secret.json from Google Cloud Console and place it at the project root.",
            status=500,
        )

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        code_challenge_method='S256',
    )

    request.session['google_state'] = state
    request.session['google_code_verifier'] = flow.code_verifier
    return redirect(authorization_url)


def google_callback(request):
    state = request.session.get('google_state')
    code_verifier = request.session.get('google_code_verifier')
    if not state:
        return HttpResponseBadRequest('Missing Google OAuth state.')
    if not code_verifier:
        return HttpResponseBadRequest('Missing Google OAuth code verifier.')

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )

    flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    request.session['google_token'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }
    request.session.pop('google_code_verifier', None)

    return redirect('upload_property')


def get_google_credentials(request):
    token_data = request.session.get('google_token')
    if not token_data:
        return None

    return Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes') or SCOPES,
    )


def google_drive_import(request, file_id):
    credentials = get_google_credentials(request)
    if not credentials:
        return redirect('google_drive_login')

    service = build('drive', 'v3', credentials=credentials)
    file_meta = service.files().get(fileId=file_id, fields='name,mimeType,webViewLink').execute()
    request_obj = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_obj)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    filename = file_meta.get('name') or 'drive-import.jpg'
    safe_name = os.path.basename(filename)
    file_dir = os.path.join(settings.MEDIA_ROOT, 'google_drive_imports')
    os.makedirs(file_dir, exist_ok=True)
    media_path = os.path.join(file_dir, safe_name)
    with open(media_path, 'wb') as f:
        f.write(fh.getvalue())

    request.session['drive_import_file'] = safe_name
    request.session['drive_import_url'] = file_meta.get('webViewLink', '')
    request.session['drive_import_media_url'] = f'/media/google_drive_imports/{safe_name}'

    return redirect('upload_property')


def upload_property(request):
    drive_files = []
    selected_drive_file = request.session.get('drive_import_file')
    selected_drive_url = request.session.get('drive_import_url')

    creds = get_google_credentials(request)
    if creds:
        try:
            service = build('drive', 'v3', credentials=creds)
            results = service.files().list(
                pageSize=10,
                fields='nextPageToken, files(id, name, mimeType, webViewLink)',
                q="mimeType contains 'image/'"
            ).execute()
            drive_files = results.get('files', [])
        except Exception:
            drive_files = []

    if request.method == 'POST':
        form = EstateForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)

            if not upload.image and selected_drive_file:
                upload.image = os.path.join('google_drive_imports', selected_drive_file)

            upload.save()
            request.session.pop('drive_import_file', None)
            request.session.pop('drive_import_url', None)
            return redirect('properties')
    else:
        form = EstateForm()
    return render(request, 'upload_property.html', {
        'form': form,
        'drive_files': drive_files,
        'selected_drive_file': selected_drive_file,
        'selected_drive_url': selected_drive_url,
        'selected_drive_media_urls': [request.session.get('drive_import_media_url')],
    })

def contact(request):
    return render(request, 'contact-us.html')

def estate_detail(request, pk):
    estate = get_object_or_404(Estate, pk=pk)
    estates = Estate.objects.all()
    google_drive_imported_file = request.session.get('drive_import_file')
    google_drive_imported_url = request.session.get('drive_import_url')
    serializer = ImageSerializer(google_drive_imported_file, many=True)
    google_drive_imports = Estate.objects.filter(google_drive_image__isnull=False)
    
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
        'estates': estates,
        'selected_drive_file': google_drive_imported_file,
        'selected_drive_url': google_drive_imported_url,
        'selected_drive_media_urls': [request.session.get('drive_import_media_url')] if google_drive_imported_file else [],
        'serializer': serializer.data if google_drive_imported_file else None,
        'google_drive_image': google_drive_imports,
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