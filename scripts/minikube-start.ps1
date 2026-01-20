# Minikube Start Script for CAP-X Platform
# Optimized for 8GB RAM and Ryzen 3 processor

Write-Host "🚀 Starting Minikube for CAP-X Platform..." -ForegroundColor Cyan

# Check if Minikube is installed
if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Minikube is not installed!" -ForegroundColor Red
    Write-Host "Please install Minikube from: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    exit 1
}

# Stop Docker Desktop Kubernetes if running
Write-Host "⚠️  Make sure Docker Desktop's Kubernetes is disabled to avoid conflicts" -ForegroundColor Yellow

# Start Minikube with optimized settings
Write-Host "Starting Minikube with optimized settings (2GB RAM, 2 CPUs)..." -ForegroundColor Green

minikube start `
    --driver=docker `
    --memory=2048 `
    --cpus=2 `
    --disk-size=10g `
    --kubernetes-version=v1.28.0 `
    --addons=ingress,metrics-server `
    --container-runtime=docker

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Minikube" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Minikube started successfully!" -ForegroundColor Green

# Enable addons
Write-Host "Enabling addons..." -ForegroundColor Cyan
minikube addons enable ingress
minikube addons enable metrics-server

# Display cluster info
Write-Host "`n📊 Cluster Information:" -ForegroundColor Cyan
kubectl cluster-info

Write-Host "`n🔧 Minikube Status:" -ForegroundColor Cyan
minikube status

Write-Host "`n💡 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\scripts\minikube-deploy.ps1 to deploy the application"
Write-Host "2. Run: minikube dashboard to open Kubernetes dashboard"
Write-Host "3. Run: minikube ip to get the cluster IP address"
Write-Host "`n⚡ To use Minikube's Docker daemon, run:"
Write-Host "   minikube docker-env | Invoke-Expression" -ForegroundColor Cyan
