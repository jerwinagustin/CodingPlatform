# Quick Start Script for Development

Write-Host "🚀 Starting University Management System..." -ForegroundColor Cyan
Write-Host ""

# Check if MongoDB is running
Write-Host "📊 Checking MongoDB..." -ForegroundColor Yellow
$mongoProcess = Get-Process mongod -ErrorAction SilentlyContinue
if ($mongoProcess) {
    Write-Host "✅ MongoDB is running" -ForegroundColor Green
} else {
    Write-Host "❌ MongoDB is not running. Please start MongoDB first!" -ForegroundColor Red
    Write-Host "   Run: mongod" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎯 Starting Django Backend..." -ForegroundColor Yellow
$djangoPath = "c:\Users\ADMIN\OneDrive\Desktop\Just for fun\django-app"

# Start Django in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$djangoPath'; python manage.py runserver" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "✅ Django backend started at http://localhost:8000" -ForegroundColor Green
Write-Host ""

Write-Host "⚛️  Starting React Frontend..." -ForegroundColor Yellow
$reactPath = "c:\Users\ADMIN\OneDrive\Desktop\Just for fun\first-app"

# Start React in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$reactPath'; npm run dev" -WindowStyle Normal

Write-Host "✅ React frontend will start at http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 All servers started!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 URLs:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Admin:    http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
