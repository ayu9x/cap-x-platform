# Minikube Deployment Script for CAP-X Platform
# Builds and deploys all services to Minikube

Write-Host "🚀 Deploying CAP-X Platform to Minikube..." -ForegroundColor Cyan

# Check if Minikube is running
$minikubeStatus = minikube status --format='{{.Host}}' 2>$null
if ($minikubeStatus -ne "Running") {
    Write-Host "❌ Minikube is not running. Please run .\scripts\minikube-start.ps1 first" -ForegroundColor Red
    exit 1
}

# Set Docker environment to use Minikube's Docker daemon
Write-Host "🔧 Configuring Docker to use Minikube's daemon..." -ForegroundColor Cyan
& minikube docker-env | Invoke-Expression

# Build Docker images
Write-Host "`n🏗️  Building Docker images..." -ForegroundColor Green

Write-Host "Building backend image..." -ForegroundColor Yellow
docker build -t capx-backend:latest ./backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Building frontend image..." -ForegroundColor Yellow
docker build -t capx-frontend:latest ./frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Building auto-healing image..." -ForegroundColor Yellow
docker build -t capx-auto-healing:latest ./auto-healing
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Auto-healing build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All images built successfully!" -ForegroundColor Green

# Create namespace
Write-Host "`n📦 Creating Kubernetes namespace..." -ForegroundColor Cyan
kubectl create namespace capx-platform --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
Write-Host "`n🚢 Deploying to Kubernetes..." -ForegroundColor Green

Write-Host "Applying secrets..." -ForegroundColor Yellow
kubectl apply -f infrastructure/kubernetes/mongodb-secret.yaml

Write-Host "Deploying backend..." -ForegroundColor Yellow
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml

Write-Host "Deploying frontend..." -ForegroundColor Yellow
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

Write-Host "Applying services..." -ForegroundColor Yellow
kubectl apply -f infrastructure/kubernetes/backend-service.yaml
kubectl apply -f infrastructure/kubernetes/frontend-service.yaml

Write-Host "Applying ingress..." -ForegroundColor Yellow
kubectl apply -f infrastructure/kubernetes/ingress.yaml

Write-Host "`n⏳ Waiting for pods to be ready..." -ForegroundColor Cyan
kubectl wait --for=condition=ready pod -l app=capx-backend -n capx-platform --timeout=120s
kubectl wait --for=condition=ready pod -l app=capx-frontend -n capx-platform --timeout=120s

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green

# Display status
Write-Host "`n📊 Deployment Status:" -ForegroundColor Cyan
kubectl get pods -n capx-platform
kubectl get services -n capx-platform

# Get Minikube IP
$minikubeIP = minikube ip
Write-Host "`n🌐 Access Information:" -ForegroundColor Yellow
Write-Host "Minikube IP: $minikubeIP" -ForegroundColor Cyan
Write-Host "Frontend: http://$minikubeIP" -ForegroundColor Cyan
Write-Host "Backend API: http://$minikubeIP/api" -ForegroundColor Cyan
Write-Host "`n💡 To access via localhost, run:" -ForegroundColor Yellow
Write-Host "   kubectl port-forward -n capx-platform service/capx-frontend-service 3000:3000" -ForegroundColor Cyan
Write-Host "   kubectl port-forward -n capx-platform service/capx-backend-service 5000:5000" -ForegroundColor Cyan
