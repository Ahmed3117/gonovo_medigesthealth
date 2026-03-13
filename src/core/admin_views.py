"""
Admin-only view: Import Demo Data
Triggered from the Django admin dashboard via a POST form button.
"""
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.core.management import call_command
import io


@method_decorator(staff_member_required, name="dispatch")
class ImportDemoDataView(View):
    """
    POST-only view that runs the seed_demo_data management command
    and redirects back to admin dashboard with a success/error message.
    """

    def post(self, request):
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can import demo data.")
            return redirect("admin:index")

        buf = io.StringIO()
        try:
            call_command("seed_demo_data", stdout=buf, stderr=buf)
            output = buf.getvalue()
            messages.success(
                request,
                (
                    "✅ Demo data imported successfully! "
                    "Student login → student@medigest.com / Student123!"
                ),
            )
        except Exception as exc:
            messages.error(request, f"❌ Import failed: {exc}")

        return redirect("admin:index")


from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class UploadFigmaDataView(View):
    """
    Publicly accessible view to upload figma_data.json and seed the testing database.
    (CSRF exempt to simplify uploading on test environments)
    """

    def get(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Figma Data</title>
            <style>
                body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f7f9fc; }
                .card { padding: 40px; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
                input[type="file"] { margin: 20px 0; }
                button { background-color: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
                button:hover { background-color: #2563eb; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Upload Figma Demo Data (JSON)</h2>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="csrfmiddlewaretoken" value="%s">
                    <input type="file" name="figma_file" accept=".json" required><br>
                    <button type="submit">Upload & Seed Data</button>
                </form>
            </div>
        </body>
        </html>
        """ % request.META.get('CSRF_COOKIE', '')
        # Simple fix for CSRF missing token in this generic HTML: Use django's get_token
        from django.middleware.csrf import get_token
        csrf_token = get_token(request)
        html = html.replace('value=""', f'value="{csrf_token}"')
        
        from django.http import HttpResponse
        return HttpResponse(html)

    def post(self, request):
        uploaded_file = request.FILES.get('figma_file')
        
        from django.http import HttpResponse

        if not uploaded_file:
            return HttpResponse("No file provided.", status=400)

        import tempfile
        import os
        import traceback
        from django.core.management import call_command
        
        # Save temp file
        fd, temp_path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            
            # Validate JSON first
            import json
            with open(temp_path, 'r') as jf:
                data = json.load(jf)
            
            # Check required fields
            if 'user' not in data:
                return HttpResponse("<h3>❌ Invalid JSON</h3><p>Missing 'user' key</p>", status=400)
            if 'email' not in data['user']:
                return HttpResponse("<h3>❌ Invalid JSON</h3><p>Missing 'email' in user data</p>", status=400)
            if 'password' not in data['user']:
                return HttpResponse("<h3>❌ Invalid JSON</h3><p>Missing 'password' in user data</p>", status=400)
            
            # Execute command
            buf = io.StringIO()
            call_command("seed_figma_data", file=temp_path, stdout=buf, stderr=buf)
            output = buf.getvalue()
            
            return HttpResponse(
                f"<h3>✅ Figma data seeded successfully!</h3><pre>{output}</pre>"
                f"<br><a href='/admin/'>Go to Admin Dashboard</a>"
            )
            
        except json.JSONDecodeError as exc:
            return HttpResponse(
                f"<h3>❌ Invalid JSON file</h3><p>{exc}</p>",
                status=400
            )
        except Exception as exc:
            tb = traceback.format_exc()
            return HttpResponse(
                f"<h3>❌ Import failed</h3><p>{exc}</p>"
                f"<h4>Traceback:</h4><pre>{tb}</pre>",
                status=500
            )
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
