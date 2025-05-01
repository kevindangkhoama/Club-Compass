from django.contrib import admin
from django.urls import path, include
from django.core.management import call_command
from django.http import HttpResponse
from django.contrib.auth.models import User

# === TEMPORARY VIEWS FOR SETUP ===
def init_site(request):
    try:
        call_command("migrate")
        call_command("collectstatic", "--noinput")
        return HttpResponse("✅ Migrations and static collection done.")
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")

def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "yourpassword123")
        return HttpResponse("✅ Superuser created. Username: admin")
    return HttpResponse("ℹ️ Admin already exists.")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('club_compass_app.urls')),

    # === TEMPORARY SETUP ROUTES (REMOVE AFTER USE) ===
    path('init/', init_site),
    path('create-admin/', create_admin),
]
