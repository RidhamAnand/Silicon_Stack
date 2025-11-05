# AI Customer Support System - Full Stack Setup

Complete setup guide for running both the React frontend and Flask backend.

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **MongoDB Atlas** account (or local MongoDB)
- **Pinecone** account
- **Grok API** key (or OpenAI-compatible API)

## 🚀 Quick Start (2 Steps)

### Step 1: Start the Backend (Flask API)

```powershell
# Navigate to project root
cd "D:\Silicon Stack\Final Master Project"

# Activate virtual environment (if using one)
# .\venv\Scripts\Activate.ps1

# Start Flask API server
python src/api/app.py
```

The backend will start on `http://localhost:5000`

### Step 2: Start the Frontend (React)

```powershell
# Open a NEW terminal window

# Navigate to frontend directory
cd "D:\Silicon Stack\Final Master Project\frontend"

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:3000`

## 🌐 Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## 📁 Project Structure

```
Final Master Project/
├── src/
│   ├── api/
│   │   └── app.py              # Flask REST API
│   ├── agents/                 # AI agents
│   ├── classification/         # Intent & entity processing
│   ├── rag/                    # RAG pipeline
│   └── main.py                 # CLI interface (old)
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── api/               # API client
│   │   └── App.jsx            # Main app
│   └── package.json
├── requirements.txt
└── .env
```

## ⚙️ Configuration

### Backend Configuration (.env)

Ensure your `.env` file in the project root contains:

```env
# Grok API
GROK_API_KEY=your_grok_api_key_here
GROK_API_BASE=https://api.x.ai/v1

# Pinecone
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=customer-support-faqs

# MongoDB
MONGODB_URI=your_mongodb_uri_here
MONGODB_DB_NAME=customer_support

# Flask
FLASK_SECRET_KEY=your-secret-key-here
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Frontend Configuration (Optional)

Create `frontend/.env` if you need custom API URL:

```env
VITE_API_URL=http://localhost:5000/api
```

## 🔧 Installation Details

### Backend Setup

```powershell
# Install Python dependencies
pip install -r requirements.txt

# Initialize databases
python scripts/setup_faqs.py
python scripts/setup_database.py

# Test configuration
python src/api/app.py
```

### Frontend Setup

```powershell
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🧪 Testing the System

### 1. Health Check

Visit: `http://localhost:5000/api/health`

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-05T...",
  "service": "AI Customer Support API"
}
```

### 2. Test Queries

Try these in the chat interface:

- **FAQ**: "What is your return policy?"
- **Order Status**: "Check order ORD-2024-001"
- **Escalation**: "I want to file a complaint"
- **General**: "Hello, can you help me?"

## 🎯 Features

### Frontend Features
- ✅ Modern React + Tailwind UI
- ✅ Real-time chat interface
- ✅ Agent status display
- ✅ Intent & entity visualization
- ✅ Topic quick-start cards
- ✅ Responsive design (mobile-friendly)
- ✅ Typing indicators
- ✅ Error handling

### Backend Features
- ✅ RESTful API with Flask
- ✅ RAG pipeline integration
- ✅ Multi-agent routing system
- ✅ Conversation state management
- ✅ Escalation handling
- ✅ Order lookup from MongoDB
- ✅ Vector search with Pinecone
- ✅ CORS enabled

## 🔄 Development Workflow

### Running Both Servers

**Option 1: Two Terminal Windows**
```powershell
# Terminal 1 - Backend
python src/api/app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option 2: Using tmux/screen (Linux/Mac)**
```bash
# Create split screen
tmux new-session -d 'python src/api/app.py'
tmux split-window -h 'cd frontend && npm run dev'
tmux attach
```

### Hot Reload

- **Backend**: Flask auto-reloads on file changes (debug mode)
- **Frontend**: Vite auto-reloads on file changes

## 🐛 Troubleshooting

### Backend Issues

**Problem**: "Configuration Error: Missing required environment variables"
```powershell
# Solution: Check .env file exists and has all required keys
cat .env
```

**Problem**: "Database connection failed"
```powershell
# Solution: Verify MongoDB URI and connection
python -c "from src.database import db_service; db_service.connect()"
```

**Problem**: Port 5000 already in use
```powershell
# Solution: Change port in .env
FLASK_PORT=5001

# Or kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Frontend Issues

**Problem**: API connection failed
```javascript
// Solution: Check backend is running and CORS is enabled
// Visit: http://localhost:5000/api/health
```

**Problem**: Port 3000 already in use
```powershell
# Solution: Kill process or change port
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or change port in vite.config.js
```

**Problem**: Module not found
```powershell
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/chat/start` | Start conversation |
| POST | `/api/chat/message` | Send message |
| POST | `/api/chat/escalate` | Escalate to ticket |
| GET | `/api/chat/history/:id` | Get history |
| GET | `/api/topics` | Get FAQ topics |

## 🚀 Production Deployment

### Backend (Flask API)

**Option 1: Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api.app:app
```

**Option 2: Docker**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/api/app.py"]
```

### Frontend (React)

**Build for production:**
```powershell
cd frontend
npm run build
```

**Deploy to:**
- **Vercel**: `vercel --prod`
- **Netlify**: Drag & drop `dist` folder
- **AWS S3**: Upload `dist` folder + CloudFront

## 📝 Development Tips

### Adding New Features

1. **Backend**: Add endpoint in `src/api/app.py`
2. **Frontend**: Add API call in `src/api/client.js`
3. **UI**: Create component in `src/components/`
4. **Test**: Use both CLI and web interface

### Debugging

**Backend logs:**
```powershell
# Flask prints to console
python src/api/app.py
```

**Frontend logs:**
```javascript
// Browser console (F12)
console.log('Debug info')
```

**Network inspection:**
- Open DevTools (F12) → Network tab
- Watch API calls and responses

## 🎨 Customization

### Changing UI Theme

Edit `frontend/tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#YOUR_COLOR',
        // ... more shades
      }
    }
  }
}
```

### Adding New Agent

1. Create agent in `src/agents/`
2. Register in router
3. Update frontend agent display

## 📚 Documentation

- [Frontend README](frontend/README.md)
- [Backend API Documentation](docs/API.md) *(create this)*
- [Agent System Guide](docs/AGENTS.md) *(create this)*

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review error logs
3. Test individual components
4. Check API endpoints manually

## 📄 License

Final Master Project - Silicon Stack

---

**Ready to start?** Run the quick start commands above! 🚀
