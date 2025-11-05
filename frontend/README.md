# AI Customer Support - React Frontend

A modern, responsive React + Tailwind CSS frontend for the AI Customer Support Agent.

## 🎨 Features

- **Modern UI/UX**: Beautiful gradient designs, smooth animations, and responsive layout
- **Real-time Chat**: Instant messaging with typing indicators
- **Agent Tracking**: Visual indicators showing which specialized agent is handling your request
- **Intent & Entity Display**: See how the AI understands and processes your queries
- **Topic Quick Start**: Click on predefined topics to start conversations quickly
- **Escalation Support**: Seamless ticket creation and escalation handling
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python backend running (see main README)

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # API client for backend communication
│   ├── components/
│   │   ├── ChatMessage.jsx    # Message bubble component
│   │   ├── ChatInput.jsx      # Message input field
│   │   ├── Header.jsx         # App header
│   │   ├── TopicCard.jsx      # Topic selection card
│   │   └── TypingIndicator.jsx # Typing animation
│   ├── App.jsx                # Main application component
│   ├── main.jsx               # React entry point
│   └── index.css              # Tailwind styles
├── index.html                 # HTML template
├── package.json               # Dependencies
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind configuration
└── postcss.config.js         # PostCSS configuration
```

## 🎯 Available Scripts

- **`npm run dev`** - Start development server on port 3000
- **`npm run build`** - Build for production
- **`npm run preview`** - Preview production build

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory (optional):

```env
VITE_API_URL=http://localhost:5000/api
```

### Backend Integration

The frontend connects to the Flask backend API. Make sure the backend is running on port 5000 (or update the proxy configuration in `vite.config.js`).

## 🎨 UI Components

### ChatMessage
Displays user and assistant messages with:
- Agent badges (FAQ Agent, Order Agent, Escalation Agent, etc.)
- Intent classification display
- Entity extraction display
- Routing path visualization
- Escalation status indicators
- Follow-up question suggestions

### ChatInput
Message input component with:
- Auto-resizing textarea
- Send button with loading state
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Disabled state during API calls

### TopicCard
Quick-start topic selection with:
- Icon-based navigation
- Hover effects
- Click to start conversation

## 🌈 Styling

Built with Tailwind CSS featuring:
- Custom color palette (primary blues)
- Gradient backgrounds
- Custom animations (typing indicator, pulse effects)
- Responsive breakpoints
- Custom scrollbar styling

## 📱 Responsive Design

- **Mobile**: Optimized layout for phones (320px+)
- **Tablet**: Enhanced layout for tablets (768px+)
- **Desktop**: Full-featured layout for desktop (1024px+)

## 🔄 State Management

The app uses React hooks for state management:
- `useState` for local component state
- `useEffect` for side effects (auto-scroll, topic loading)
- `useRef` for DOM references (scroll anchor)

## 🚀 Production Build

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Preview the build:**
   ```bash
   npm run preview
   ```

3. **Deploy:**
   The `dist` folder contains the production build ready for deployment to:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Any static hosting service

## 🔗 API Endpoints Used

- `POST /api/chat/start` - Start new conversation
- `POST /api/chat/message` - Send message
- `POST /api/chat/escalate` - Escalate to ticket creation
- `GET /api/chat/history/:sessionId` - Get conversation history
- `GET /api/topics` - Get available topics
- `GET /api/health` - Health check

## 🐛 Troubleshooting

### Port Already in Use
If port 3000 is already in use:
```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or change port in vite.config.js
```

### API Connection Issues
- Ensure Flask backend is running on port 5000
- Check CORS configuration in backend
- Verify API URL in `src/api/client.js`

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🎨 Customization

### Changing Colors
Edit `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### Adding New Features
1. Create component in `src/components/`
2. Import and use in `App.jsx`
3. Add API calls in `src/api/client.js` if needed

## 📄 License

Part of the Final Master Project - AI Customer Support System

## 🤝 Contributing

This is a student project. For contributions, please follow the project guidelines.
