
# 🧠 Soluna: Your AI Therapist

Soluna is an empathetic AI-powered therapist web app built using Django and enhanced with speech recognition and human-like voice replies. It helps users have thoughtful, therapeutic conversations in real time, offering support through both text and voice.




## ✨ Features

- 💬 Interactive Chat Interface – Ask anything, get empathetic responses.
- 🗣️ Voice-to-Text Input – Talk to Soluna using your voice via Web Speech API.
- 🔊 Human-like Text-to-Speech – Soluna responds with realistic speech using ElevenLabs TTS.
- 🔁 Real-Time Feedback – Continuous voice recognition without needing to click again.
- 🧠 Memory-Aware – Maintains the last few messages to provide coherent, context-aware replies.
- 🔐 User Authentication – Register, login, and chat securely.
- 🎨 Clean, Friendly UI – Built with responsive HTML/CSS templates and animations.


## 🛠️ Tech Stack

**Client:** HTML/CSS/JS

**Server:** Django

**Ai Engine:** OpenRouter (LLaMA 3.3)

**Voice Api:** ElevenLabs (TTS) / Web Speech API

**Extras:** CSRF Protection, Markdown Support


## Installation

1. Clone the Repository

```bash
  git clone https://github.com/yourusername/soluna-ai-therapist.git
  cd soluna-ai-therapist
```

2. Set up the Backend (Django)
Install dependencies
```bash
  pip install -r requirements.txt
```
Configure environment
- Add your OpenRouter API key
- Add your ElevenLabs API key
    
Run the server
- python manage.py runserver

## 📜 License

This project is open source under the MIT License.


## 💡 Inspiration

Soluna is built with the belief that mental health support should be accessible, private, and empathetic—whenever you need it.
