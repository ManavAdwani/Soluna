from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage
import requests
import json
import re
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@csrf_exempt
def elevenlabs_tts(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "")

        if not text:
            return JsonResponse({"error": "No text provided."}, status=400)

        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Example: "Rachel", replace with your chosen voice ID
        api_key = "sk_9d15b2f071ff3b84c560ae7177946bbca3def1ead20690a1"

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }

        body = {
            "text": text,
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.9
            }
        }

        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers=headers,
            json=body
        )

        if response.status_code != 200:
            return JsonResponse({"error": "TTS failed."}, status=500)

        return HttpResponse(response.content, content_type="audio/mpeg")


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after register
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def markdown_to_html(text):
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Convert newlines to <br> for line breaks
    text = text.replace('\n', '<br>')
    return text

@login_required
def home(request):
    return render(request, 'home.html')


@csrf_exempt
@login_required
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_prompt = data.get("prompt")

        # Hybrid memory: recent 5 messages for the logged-in user only
        recent_chats = ChatMessage.objects.filter(user=request.user).order_by("-created_at")[:5]
        messages = [
            {"role": "system", "content": "You are a warm and empathetic therapist. Respond briefly and supportively. Keep answers short unless the user clearly needs a deeper explanation."},
        ]
        for chat in reversed(recent_chats):  # maintain chronological order
            messages.append({"role": "user", "content": chat.user_input})
            messages.append({"role": "assistant", "content": chat.ai_response})

        messages.append({"role": "user", "content": user_prompt})

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8000/",
                "X-Title": "AI Therapist"
            },
            json={
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": messages,
            },
        )

        raw_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        formatted_response = markdown_to_html(raw_response)

        # Save chat only for the current user
        ChatMessage.objects.create(
            user=request.user,
            user_input=user_prompt,
            ai_response=raw_response
        )

        return JsonResponse({"response": formatted_response})