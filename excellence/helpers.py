from google.oauth2.credentials import Credentials

def get_google_credentials(request):
    """
    Retrieve Google API credentials from the session.
    If not found, redirect to the Google Drive login page.
    """
    credentials_data = request.session.get('google_credentials')
    if not credentials_data:
        return None  # No credentials found in session

    try:
        credentials = Credentials.from_authorized_user_info(credentials_data)
        return credentials
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None