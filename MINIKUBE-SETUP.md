# CAP-X Platform - Minikube Setup Guide

## System Requirements

### Minimum Requirements
- **RAM**: 8GB (Minikube configured to use 2GB)
- **CPU**: Dual-core processor (Ryzen 3 or equivalent)
- **Disk**: 10GB free space
- **OS**: Windows 10/11, macOS, or Linux

### Software Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed (for Docker driver)
- PowerShell 5.1 or later (Windows)

## Quick Start with Minikube

### 1. Start Minikube

```powershell
# Navigate to project directory
cd c:\Users\rajay\Desktop\Cloud\cap-x-platform

# Start Minikube with optimized settings
.\scripts\minikube-start.ps1
```

This will:
- Start Minikube with 2GB RAM and 2 CPUs
- Enable ingress and metrics-server addons
- Configure Kubernetes v1.28.0

### 2. Deploy the Application

```powershell
# Build images and deploy to Minikube
.\scripts\minikube-deploy.ps1
```

This will:
- Build Docker images in Minikube's Docker context
- Create the `capx-platform` namespace
- Deploy backend, frontend, and supporting services
- Wait for pods to be ready

### 3. Access the Application

```powershell
# Get Minikube IP
minikube ip

# Access via Minikube IP
# Frontend: http://<minikube-ip>
# Backend API: http://<minikube-ip>/api

# OR use port forwarding for localhost access
kubectl port-forward -n capx-platform service/capx-frontend-service 3000:3000
kubectl port-forward -n capx-platform service/capx-backend-service 5000:5000

# Then access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/api
```

### 4. Stop Minikube

```powershell
# Stop or delete Minikube cluster
.\scripts\minikube-stop.ps1
```

## Alternative: Lightweight Docker Compose

For even lower resource usage, use the lightweight Docker Compose configuration:

```powershell
# Start lightweight services (MongoDB, Backend, Frontend, Redis only)
docker-compose -f docker-compose.lite.yml up -d

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/api

# Stop services
docker-compose -f docker-compose.lite.yml down
```

## Resource Allocation

### Minikube Configuration
- **Minikube VM**: 2GB RAM, 2 CPUs
- **Backend Pod**: 128Mi request, 256Mi limit
- **Frontend Pod**: 64Mi request, 128Mi limit
- **Total Kubernetes**: ~2.5GB RAM usage

### What's Excluded
To optimize for 8GB RAM, the following services are **disabled by default**:
- ❌ Elasticsearch & Kibana (ELK stack) - too resource-intensive
- ⚠️ Prometheus & Grafana - optional, commented out in lite version

## Useful Commands

### Minikube Management
```powershell
# Check Minikube status
minikube status

# Open Kubernetes dashboard
minikube dashboard

# SSH into Minikube VM
minikube ssh

# View Minikube logs
minikube logs

# Delete and start fresh
minikube delete
.\scripts\minikube-start.ps1
```

### Kubernetes Commands
```powershell
# View all pods
kubectl get pods -n capx-platform

# View pod logs
kubectl logs -n capx-platform -l app=capx-backend --tail=50

# Describe a pod (for debugging)
kubectl describe pod -n capx-platform <pod-name>

# Restart a deployment
kubectl rollout restart deployment/capx-backend -n capx-platform

# Delete all pods (they'll be recreated)
kubectl delete pods -n capx-platform --all
```

### Docker Commands (in Minikube context)
```powershell
# Use Minikube's Docker daemon
minikube docker-env | Invoke-Expression

# List images in Minikube
docker images

# Build image in Minikube
docker build -t capx-backend:latest ./backend
```

## Troubleshooting

### Minikube won't start
```powershell
# Delete existing cluster and start fresh
minikube delete
minikube start --driver=docker --memory=2048 --cpus=2
```

### Pods stuck in ImagePullBackOff
```powershell
# Make sure you're using Minikube's Docker daemon
minikube docker-env | Invoke-Expression

# Rebuild images
docker build -t capx-backend:latest ./backend
docker build -t capx-frontend:latest ./frontend

# Restart deployment
kubectl rollout restart deployment/capx-backend -n capx-platform
```

### Out of Memory errors
```powershell
# Reduce replicas further or use docker-compose.lite.yml instead
docker-compose -f docker-compose.lite.yml up -d
```

### Backend pods crashing
```powershell
# Check logs
kubectl logs -n capx-platform -l app=capx-backend --tail=100

# Common issues:
# 1. MongoDB secret not created - run: kubectl apply -f infrastructure/kubernetes/mongodb-secret.yaml
# 2. Blueprint import errors - fixed in latest code
```

## Performance Tips

1. **Close unnecessary applications** while running Minikube
2. **Use docker-compose.lite.yml** for development instead of full Kubernetes
3. **Stop Minikube** when not in use: `minikube stop`
4. **Disable Docker Desktop's Kubernetes** to avoid conflicts
5. **Monitor resource usage** with Task Manager or `minikube dashboard`

## Next Steps

- Configure MongoDB connection string in secrets
- Set up ingress for external access
- Deploy to cloud (AWS EKS, GCP GKE) for production
- Enable monitoring (Prometheus/Grafana) on higher-spec machines
