# Minikube Stop Script for CAP-X Platform

Write-Host "🛑 Stopping Minikube..." -ForegroundColor Yellow

# Check if Minikube is running
$minikubeStatus = minikube status --format='{{.Host}}' 2>$null
if ($minikubeStatus -ne "Running") {
    Write-Host "ℹ️  Minikube is not running" -ForegroundColor Cyan
    exit 0
}

# Option to delete or just stop
$choice = Read-Host "Do you want to (S)top or (D)elete Minikube cluster? [S/D]"

if ($choice -eq "D" -or $choice -eq "d") {
    Write-Host "🗑️  Deleting Minikube cluster..." -ForegroundColor Red
    minikube delete
    Write-Host "✅ Minikube cluster deleted" -ForegroundColor Green
} else {
    Write-Host "⏸️  Stopping Minikube..." -ForegroundColor Yellow
    minikube stop
    Write-Host "✅ Minikube stopped" -ForegroundColor Green
    Write-Host "💡 To start again, run: .\scripts\minikube-start.ps1" -ForegroundColor Cyan
}
