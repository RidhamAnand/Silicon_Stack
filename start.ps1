# Quick Start Script for Windows PowerShell
# Run this to start both frontend and backend

Write-Host "🚀 Starting AI Customer Support System..." -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "src\api\app.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    pause
    exit 1
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    pause
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    pause
    exit 1
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Please create it from .env.example" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "Starting Backend (Flask API)..." -ForegroundColor Cyan

# Start Flask in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python src\api\app.py"

Write-Host "✅ Backend starting on http://localhost:5000" -ForegroundColor Green
Write-Host ""

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host "Starting Frontend (React)..." -ForegroundColor Cyan

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Start React in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "✅ Frontend starting on http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Both servers are starting!" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (servers will keep running)..." -ForegroundColor Yellow
pause
