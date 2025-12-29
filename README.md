# 🌙 Soluna - AI Therapist

<div align="center">
  <img src="https://i.ibb.co/KjtG8Pq8/Capture.png" alt="Soluna Dashboard" width="100%" />
</div>

## 📖 Overview
**Soluna** is a compassionate AI-powered therapy assistant designed to provide a safe, private, and supportive space for users. It combines advanced Large Language Models (LLM) with voice interaction to create a seamless therapeutic experience.

## 💡 Inspiration
Soluna is built with the belief that mental health support should be accessible, private, and empathetic—whenever you need it.

## ✨ Key Features

### 🎙️ Immersive Voice Mode
Talk to Soluna naturally using your voice.
- **Speech-to-Text**: Instant transcription of your spoken words.
- **Text-to-Speech**: High-quality, soothing voice responses via ElevenLabs.
- **Visualizer**: Dynamic "Orb" animation that reacts to listening and speaking states.

### 💬 Intelligent Chat & History
- **Session Management**: Organized conversation history (ChatGPT-style).
- **Context Awareness**: Remembers the context of your current session.
- **Sidebar**: Easy navigation between past conversations with "New Chat" and "Delete" options.
- **Premium UI**: Glassmorphic design with smooth transitions and centered layout.

### 📊 Emotional Dashboard
- **Mood Tracking**: Automatically analyzes the sentiment of your conversations (-1 to +1 scale).
- **Interactive Charts**: Visualizes mood trends over the last 7 days.
- **Emotion Mix**: Doughnut chart breaking down specific emotions (Happy, Anxious, Neutral, etc.).
- **Key Stats**: Quick overview of total sessions and messages exchanged.

### 📓 Soluna Journal
- **AI Reflections**: Write your thoughts, and Soluna will provide a private, supportive reflection (not advice) to help you gain perspective.
- **Smart Layout**:
  - **Desktop**: Split-screen view (Past entries vs. Editor).
  - **Mobile**: Intuitive Tab system ([Write] | [History]) for distraction-free journaling.
- **Secure Storage**: All entries are private and stored securely.

### 🧘 Therapeutic Exercises
- **Integrated Videos**: Curated therapeutic exercises (e.g., Box Breathing, Grounding).
- **Smart suggestions**: The AI recommends specific exercises based on your emotional state.

## 🛠️ Tech Stack
- **Backend**: Django 5.1 (Python)
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS
- **Database**: MySQL
- **AI Engine**: Meta Llama 3.3 70B (via OpenRouter)
- **Voice**: ElevenLabs API / Web Speech API

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/soluna.git
   cd soluna
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Ensure MySQL is running and create a database named `ai_therapist`.
   ```bash
   python manage.py migrate
   ```

4. **Run the Server**
   ```bash
   python manage.py runserver
   ```

## 🛡️ License
This project is licensed under the MIT License.
