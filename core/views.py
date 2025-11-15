# seu_app/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from .forms import EmailUploadForm
from .models import EmailAnalysis
from .services import extract_text_from_file, preprocess_text, ai_classify_and_respond


@require_http_methods(["GET", "POST"])
def home(request: HttpRequest):
    result = None

    if request.method == "POST":
        form = EmailUploadForm(request.POST, request.FILES)

        if form.is_valid():
            email_file = form.cleaned_data.get('email_file')
            email_text = form.cleaned_data.get('email_text')
            if email_file:
                raw_text = extract_text_from_file(email_file)
            else:
                raw_text = email_text

            if not raw_text.strip():
                result = None
            else:
                processed_text = preprocess_text(raw_text)
                category, suggested_response = ai_classify_and_respond(processed_text)
                analysis = EmailAnalysis.objects.create(
                    original_text=raw_text,
                    category=category,
                    suggested_response=suggested_response,
                )

                result = analysis
    else:
        form = EmailUploadForm()

    return render(request, "core/home.html", {"form": form, "result": result})