from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta
from .models import ChatMessage, Conversation
import requests
import json
import re


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
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
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
    
    # Convert [VIDEO: https://www.youtube.com/watch?v=...] to embedded iframe
    # Matches standard YouTube URLs and shortened youtu.be URLs
    youtube_regex = r'\[VIDEO:\s*(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+))\]'
    
    def embed_youtube(match):
        video_url = match.group(0).replace('[VIDEO: ', '').replace(']', '') # Simplistic extraction for fallback
        video_id = match.group(2)
        return (
            f'<div class="my-4 w-full flex flex-col items-center">'
            f'<div class="w-full aspect-w-16 aspect-h-9 relative">'
            f'<iframe class="w-full h-64 rounded-xl shadow-lg" src="https://www.youtube.com/embed/{video_id}" '
            f'title="YouTube video player" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
            f'</div>'
            f'<a href="https://www.youtube.com/watch?v={video_id}" target="_blank" class="mt-2 text-indigo-500 hover:text-indigo-700 text-sm font-medium flex items-center gap-1">'
            f'<i class="fas fa-external-link-alt"></i> Watch on YouTube (if playback fails)'
            f'</a>'
            f'</div>'
        )
    
    text = re.sub(youtube_regex, embed_youtube, text)
    
    # Convert newlines to <br> for line breaks
    text = text.replace('\n', '<br>')
    return text

@login_required
def home(request):
    return render(request, 'home.html')


from .models import ChatMessage, Conversation

@csrf_exempt
@login_required
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_prompt = data.get("prompt")
        conversation_id = data.get("conversation_id")

        # 1. Handle Conversation ID
        conversation = None
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            except Conversation.DoesNotExist:
                pass # Fallback to new
        
        if not conversation:
            # Create title from first few words of prompt
            title = " ".join(user_prompt.split()[:5]) + "..."
            conversation = Conversation.objects.create(user=request.user, title=title)
        
        # 2. Hybrid memory: scoped to THIS conversation
        recent_chats = ChatMessage.objects.filter(conversation=conversation).order_by("-created_at")[:5]
        
        messages = [
            {"role": "system", "content": "You are a warm, empathetic, and professional therapist named Soluna. Your goal is to support the user through active listening and gentle guidance.\n\nIMPORTANT: If the user is anxious, stressed, or asks for help with exercises, you SHOULD suggest simple therapeutic exercises. \n\nWHEN YOU SUGGEST AN EXERCISE, YOU MUST USE ONE OF THESE SPECIFIC VIDEOS (do not make up others):\n\n1. For Grounding (5-4-3-2-1): `[VIDEO: https://www.youtube.com/watch?v=30VMIEmA114]`\n2. For Box Breathing: `[VIDEO: https://www.youtube.com/watch?v=FJJazKtH_9I]`\n3. For Muscle Relaxation: `[VIDEO: https://www.youtube.com/watch?v=ihO02wUzgkc]`\n\nExample response: 'I can help with that. Let's try a grounding technique. [VIDEO: https://www.youtube.com/watch?v=30VMIEmA114]'\n\nKeep other responses brief/concise unless a deeper explanation is needed."},
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

        print(response)

        raw_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        
        formatted_response = markdown_to_html(raw_response)
        
        # Analyze Sentiment
        sentiment_score, emotion_label = analyze_sentiment(user_prompt)

        # Save chat only for the current user
        ChatMessage.objects.create(
            user=request.user,
            conversation=conversation,
            user_input=user_prompt,
            ai_response=raw_response,
            sentiment_score=sentiment_score,
            emotion_label=emotion_label
        )
       

        return JsonResponse({
            "response": formatted_response,
            "raw_message": raw_response,
            "conversation_id": conversation.id,
            "conversation_title": conversation.title
        })

@login_required
def get_conversations(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at').values('id', 'title', 'updated_at')
    return JsonResponse({"conversations": list(conversations)})

@login_required
def load_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        messages = ChatMessage.objects.filter(conversation=conversation).order_by('created_at')
        
        chat_history = []
        for msg in messages:
            chat_history.append({"role": "user", "content": msg.user_input})
            chat_history.append({"role": "therapist", "content": markdown_to_html(msg.ai_response)})
            
        return JsonResponse({"messages": chat_history, "title": conversation.title})
    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found"}, status=404)

@csrf_exempt
@login_required
def delete_conversation(request, conversation_id):
    if request.method == "DELETE":
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            conversation.delete()
            return JsonResponse({"success": True})
        except Conversation.DoesNotExist:
            return JsonResponse({"error": "Conversation not found"}, status=404)
    return JsonResponse({"error": "Invalid method"}, status=405)

# --- Analytics Logic ---

def analyze_sentiment(text):
    """
    Simple keyword-based sentiment analyzer.
    Returns (score, label).
    Score: -1.0 to 1.0
    """
    text = text.lower()
    
    # Simple lexicon
    positive_words = ["happy", "good", "great", "excellent", "love", "wonderful", "calm", "relaxed", "better", "thanks", "thank", "hope", "joy", "excited", "progress", "proud"]
    negative_words = ["sad", "bad", "terrible", "awful", "hate", "angry", "anxious", "depressed", "stressed", "worse", "tired", "lonely", "fear", "scared", "pain", "hurt"]
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    total = pos_count + neg_count
    if total == 0:
        return 0.0, "Neutral"
    
    score = (pos_count - neg_count) / total # Normalize between -1 and 1 (roughly)
    # Scale for intensity if needed, but ratio is fine for now
    
    if score > 0.3:
        label = "Positive"
    elif score < -0.3:
        label = "Negative"
    else:
        label = "Neutral"
        
    # Refine labels based on specific keywords
    if "anxious" in text or "stress" in text:
        label = "Anxious"
    elif "sad" in text or "lonely" in text:
        label = "Sad"
    elif "happy" in text or "excited" in text:
        label = "Happy"
        
    return score, label

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required
def dashboard_api(request):
    # Get last 7 days data
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    
    messages = ChatMessage.objects.filter(
        user=request.user, 
        created_at__range=[start_date, end_date]
    ).order_by('created_at')
    
    # 1. Daily Average Sentiment
    daily_stats = {}
    for i in range(7):
        date_label = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_stats[date_label] = {"total_score": 0, "count": 0}
        
    for msg in messages:
        date_str = msg.created_at.strftime("%Y-%m-%d")
        if date_str in daily_stats:
            daily_stats[date_str]["total_score"] += msg.sentiment_score
            daily_stats[date_str]["count"] += 1
            
    dates = []
    scores = []
    # Reverse to show chronological order
    sorted_dates = sorted(daily_stats.keys())
    for date in sorted_dates:
        stat = daily_stats[date]
        avg = stat["total_score"] / stat["count"] if stat["count"] > 0 else 0
        dates.append(date)
        scores.append(round(avg, 2))
        
    # 2. Emotion Distribution
    emotion_counts = {}
    total_msgs = messages.count()
    
    for msg in messages:
        label = msg.emotion_label
        emotion_counts[label] = emotion_counts.get(label, 0) + 1
        
    # 3. Recent Mood (Last Message)
    last_msg = messages.last()
    recent_mood = last_msg.emotion_label if last_msg else "Neutral"
        
    return JsonResponse({
        "dates": dates,
        "scores": scores,
        "emotion_labels": list(emotion_counts.keys()),
        "emotion_data": list(emotion_counts.values()),
        "total_sessions": request.user.conversations.count(),
        "total_messages": total_msgs,
        "recent_mood": recent_mood
    })

# --- Journaling Logic ---
from .models import JournalEntry

@login_required
def journal_view(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'journal.html', {'entries': entries})

@login_required
def save_journal_entry(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "")
        
        if not content.strip():
             return JsonResponse({"error": "Content cannot be empty"}, status=400)
             
        # Generate AI Reflection
        # Reusing the OpenRouter logic (simplified)
        API_KEY = "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"
        
        system_prompt = "You are a supportive, empathetic therapy AI. Read the user's journal entry and provide a short, deep, validating reflection (max 3 sentences). Do not give advice, just reflect on their feelings."
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.3-70b-instruct:free", 
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content}
                    ]
                }
            )
            ai_reflection = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Thank you for sharing your thoughts.")
        except Exception as e:
            print(f"Error generating reflection: {e}")
            ai_reflection = "Thank you for sharing. I'm listening."
            
        # Save Entry
        entry = JournalEntry.objects.create(
            user=request.user,
            content=content,
            ai_reflection=ai_reflection
        )
        
        return JsonResponse({
            "id": entry.id,
            "date": entry.created_at.strftime("%b %d, %Y"), # e.g. "Dec 29, 2025"
            "content": entry.content,
            "reflection": entry.ai_reflection
        })
        
    return JsonResponse({"error": "Invalid method"}, status=405)