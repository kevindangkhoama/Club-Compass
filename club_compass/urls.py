from django.contrib import admin
from django.urls import path, include
from django.core.management import call_command
from django.http import HttpResponse
from django.contrib.auth.models import User

# === TEMPORARY VIEWS FOR SETUP ===
def init_site(request):
    from io import StringIO
    from django.core.management import call_command

    output = StringIO()
    try:
        call_command("showmigrations", stdout=output)
        call_command("migrate", verbosity=2, stdout=output)
        call_command("collectstatic", "--noinput", verbosity=2, stdout=output)
        output.write("\n✅ Done!")
    except Exception as e:
        output.write(f"\n❌ ERROR: {str(e)}")

    return HttpResponse(f"<pre>{output.getvalue()}</pre>")

from club_compass_app.views import migrate_view

urlpatterns = [
    # other paths...
    path("run-migrations/", migrate_view),
]

def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "yourpassword123")
        return HttpResponse("✅ Superuser created. Username: admin")
    return HttpResponse("ℹ️ Admin already exists.")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('', include("club_compass_app.urls")),

    # TEMPORARY ROUTES
    path('init/', init_site),
    path('create-admin/', create_admin),
]
