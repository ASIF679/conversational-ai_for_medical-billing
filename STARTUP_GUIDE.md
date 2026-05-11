# 🚀 MedCare AI - Startup Guide

## 📋 Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- PostgreSQL database running (or use SQLite for development)

## 🔧 Backend Setup

### 1. Install Dependencies
```bash
cd e:\Projects\conversational-ai_for_medical-billing
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost/medcare_db
GROQ_API_KEY=your_groq_api_key_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
```

### 3. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python seed_data.py
```

### 4. Start Backend Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://127.0.0.1:8000`

## 🎨 Frontend Setup

### 1. Navigate to Frontend
```bash
cd e:\Projects\conversational-ai_for_medical-billing\frontend\artifacts\medical-billing-ai
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Frontend Server
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🔌 API Connections

### ✅ Connected Endpoints:
- **Chat API**: `http://127.0.0.1:8000/chat/` - Real-time AI chat
- **Voice API**: `http://127.0.0.1:8000/voice/chat-audio` - Voice interaction
- **Transcription**: `http://127.0.0.1:8000/voice/transcribe` - Speech-to-text
- **Text-to-Speech**: `http://127.0.0.1:8000/voice/speak` - AI voice response
- **Appointments**: `http://127.0.0.1:8000/appointments/book` - Booking system
- **Health Check**: `http://127.0.0.1:8000/Health` - Server status

## 🎯 Features Working

### ✅ Chat Interface
- Real-time AI conversation with session management
- Voice input with transcription
- File upload support
- Error handling and connection status

### ✅ Voice Calls
- Live voice interaction with AI
- Waveform visualization
- Recording controls (mute, speaker, end call)
- Real-time transcription display

### ✅ UI Components
- Modern SaaS-style design
- Responsive layout
- Dark theme with glassmorphism
- Smooth animations and transitions

## 🧪 Testing

### Test Chat API:
```bash
curl -X POST "http://127.0.0.1:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Hello, what can you help me with?"}'
```

### Test Voice API:
```bash
curl -X POST "http://127.0.0.1:8000/voice/transcribe" \
  -F "audio=@test_audio.webm"
```

### Health Check:
```bash
curl "http://127.0.0.1:8000/Health"
```

## 🚨 Troubleshooting

### Backend Issues:
1. **ModuleNotFoundError**: Install missing dependencies with `pip install -r requirements.txt`
2. **Database Connection**: Check DATABASE_URL in .env file
3. **Groq API Key**: Ensure valid GROQ_API_KEY is set

### Frontend Issues:
1. **404 Errors**: Ensure backend is running on port 8000
2. **CORS Issues**: Backend should handle CORS automatically
3. **Voice Recording**: Allow microphone permissions in browser

### Common Solutions:
- Restart both servers after configuration changes
- Check browser console for detailed error messages
- Verify all environment variables are set correctly
- Ensure PostgreSQL is running if using PostgreSQL

## 🎉 Success Indicators

You should see:
- ✅ Backend server running on `http://127.0.0.1:8000`
- ✅ Frontend running on `http://localhost:5173`
- ✅ Chat interface responding to messages
- ✅ Voice controls working with microphone access
- ✅ Real-time waveform visualization during calls
- ✅ AI responses appearing in chat and voice interfaces

## 📞 Support

If you encounter issues:
1. Check the server logs for detailed error messages
2. Verify all API endpoints are accessible
3. Test individual endpoints with curl commands
4. Check browser developer tools for frontend errors

Your MedCare AI system is now ready to use! 🎊
