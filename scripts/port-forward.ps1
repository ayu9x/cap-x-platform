# Port Forward Script for CAP-X Platform
# Opens port forwards in separate PowerShell windows

Write-Host "🌐 Starting port forwards for CAP-X Platform..." -ForegroundColor Cyan

# Check if services exist
$services = kubectl get service -n capx-platform -o name 2>$null
if (-not $services) {
    Write-Host "❌ No services found in capx-platform namespace" -ForegroundColor Red
    Write-Host "💡 Run .\scripts\minikube-deploy.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Start backend port forward in new window
Write-Host "Starting backend port forward (5000:5000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward -n capx-platform service/capx-backend-service 5000:5000"

# Wait a moment
Start-Sleep -Seconds 2

# Start frontend port forward in new window
Write-Host "Starting frontend port forward (3000:3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward -n capx-platform service/capx-frontend-service 3000:3000"

Write-Host "`n✅ Port forwards started!" -ForegroundColor Green
Write-Host "`n🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend API: http://localhost:5000/api" -ForegroundColor Yellow
Write-Host "   Health Check: http://localhost:5000/health" -ForegroundColor Yellow

Write-Host "`n💡 Close the port forward windows to stop forwarding" -ForegroundColor Cyan
