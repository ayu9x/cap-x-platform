# 🚀 CAP-X: Cloud Autonomous Platform

<div align="center">

![CAP-X Banner](https://img.shields.io/badge/CAP--X-Cloud%20Autonomous%20Platform-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Enterprise-Grade Internal Developer Platform with AI-Assisted Operations**

[Features](#-key-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Detailed Setup](#-detailed-setup)
- [Database Schema](#-database-schema)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Monitoring & Observability](#-monitoring--observability)
- [Auto-Healing](#-auto-healing)
- [Security](#-security)
- [Interview Guide](#-interview-guide)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

CAP-X is a **next-generation Internal Developer Platform (IDP)** inspired by platforms used at FAANG companies like Google (Borg), Netflix (Spinnaker), and Amazon (AWS Service Catalog). It provides a unified interface for developers to deploy, monitor, and manage applications across multi-cloud environments.

### What Makes CAP-X Special?

- 🤖 **AI-Assisted Operations**: Automatic anomaly detection and intelligent remediation
- 🔄 **Self-Healing**: Automatic incident detection and resolution
- 📊 **Real-Time Observability**: Prometheus + Grafana + ELK Stack
- 🎨 **Futuristic UI**: Dark-mode glassmorphic design with real-time animations
- 💾 **Persistent Storage**: MongoDB for all operational data
- ☸️ **Kubernetes Native**: Full integration with K8s for orchestration
- 🔐 **Enterprise Security**: RBAC, JWT auth, audit logging
- 📈 **Production Ready**: Horizontal scaling, auto-healing, CI/CD integrated

---

## ✨ Key Features

### 1. Application Management
- 📦 Service registry and catalog
- 🔄 Multi-environment support (dev/staging/prod)
- 📝 Application health tracking
- 🏷️ Metadata and tagging system

### 2. Deployment Automation
- 🚀 One-click deployments
- 🔄 Rolling, blue-green, and canary strategies
- 📊 Deployment history and tracking
- ⏪ Automatic rollback on failure
- 📈 Success rate analytics

### 3. CI/CD Integration
- 🔗 GitHub Actions integration
- 🔧 Pipeline execution tracking
- 📋 Build and test automation
- 🎯 Multi-stage deployments

### 4. Infrastructure as Code
- 🏗️ Terraform for AWS provisioning
- 📝 State management with S3 + DynamoDB
- 🔄 Infrastructure drift detection
- 📊 Resource tracking

### 5. Monitoring & Alerting
- 📊 Prometheus metrics collection
- 📈 Grafana dashboards
- 🚨 Real-time alerting
- 📉 SLO/SLA tracking

### 6. Centralized Logging
- 📝 ELK Stack integration
- 🔍 Full-text log search
- 📊 Log aggregation and analysis
- 🎯 Custom log parsing

### 7. Auto-Healing & Reliability
- 🤖 Automatic incident detection
- 🔧 Self-remediation scripts
- 📊 MTTR (Mean Time To Resolve) tracking
- 📈 Incident timeline and history

### 8. Security & Governance
- 🔐 JWT-based authentication
- 👥 Role-based access control (RBAC)
- 📋 Complete audit logging
- 🔒 Secrets management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   React Dashboard                        │
│          (Futuristic Dark Mode UI)                      │
│  Components: Dashboard, Apps, Pipelines, Monitoring     │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API (JWT Auth)
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Backend (Python)                      │
│  Routes: Auth | Apps | Deployments | Incidents         │
│  Services: Terraform | Kubernetes | CI/CD | Healing    │
└──────────────────────┬──────────────────────────────────┘
                       │ PyMongo
                       ▼
┌─────────────────────────────────────────────────────────┐
│               MongoDB Database                           │
│  Collections: users, applications, deployments,         │
│  incidents, pipelines, metrics, audit_logs              │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        ▼             ▼              ▼              ▼
   ┌────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐
   │Terraform│   │Kubernetes│   │ GitHub  │   │Prometheus│
   │ (AWS)  │   │  (EKS)   │   │ Actions │   │ Grafana  │
   └────────┘   └──────────┘   └─────────┘   └──────────┘
```

### Data Flow

1. **User Interaction**: Developer interacts with React dashboard
2. **API Gateway**: Flask handles requests, validates JWT tokens
3. **Business Logic**: Services orchestrate Terraform, Kubernetes, CI/CD
4. **Data Persistence**: All operations logged to MongoDB
5. **Infrastructure**: Terraform provisions AWS resources
6. **Orchestration**: Kubernetes manages containerized workloads
7. **Monitoring**: Prometheus collects metrics, Grafana visualizes
8. **Auto-Healing**: Background service detects and remediates issues

---

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: Flask 3.0
- **Database**: MongoDB 7.0
- **Auth**: JWT (PyJWT)
- **Kubernetes Client**: kubernetes-python
- **AWS SDK**: boto3

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Charts**: Recharts
- **HTTP Client**: Axios

### Infrastructure
- **IaC**: Terraform 1.6+
- **Cloud**: AWS (Free Tier Compatible)
- **Container Orchestration**: Kubernetes 1.28+
- **Container Registry**: Amazon ECR / Docker Hub
- **CI/CD**: GitHub Actions

### Monitoring & Logging
- **Metrics**: Prometheus 2.x
- **Visualization**: Grafana 10.x
- **Logging**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **Tracing**: OpenTelemetry (Future)

### DevOps Tools
- **Containerization**: Docker 24.x
- **Orchestration**: Kubernetes 1.28+
- **Version Control**: Git
- **Package Manager**: pip, npm

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (with Kubernetes enabled)
- Python 3.11+
- Node.js 18+
- MongoDB (Atlas or Local)
- Git

### One-Command Setup (Docker Compose)

```bash
# Clone repository
git clone https://github.com/your-org/cap-x-platform.git
cd cap-x-platform

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your MongoDB URI

# Start all services
docker-compose up -d

# Access the platform
# Dashboard: http://localhost:3000
# Backend API: http://localhost:5000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### Default Credentials

```
Email: admin@capx.io
Password: Admin@123
```

**⚠️ Change default password immediately in production!**

---

## 📖 Detailed Setup

### Step 1: MongoDB Setup

#### Option A: MongoDB Atlas (Recommended)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create M0 Free Cluster
3. Configure Network Access (Allow 0.0.0.0/0 for dev)
4. Create Database User
5. Get connection string

#### Option B: Local MongoDB

```bash
# Windows (with Chocolatey)
choco install mongodb

# macOS
brew install mongodb-community

# Linux
sudo apt-get install mongodb
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run backend
python app.py
```

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Step 4: Infrastructure Setup (Optional)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan

# Apply infrastructure
terraform apply
```

---

## 🗄️ Database Schema

### Collections Overview

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| **users** | Authentication & RBAC | email, role, permissions |
| **applications** | Service registry | name, status, environments |
| **deployments** | Deployment history | version, status, environment |
| **pipelines** | CI/CD pipeline runs | status, duration, logs |
| **incidents** | Auto-healing incidents | severity, status, timeline |
| **metrics** | Application metrics | cpu, memory, latency |
| **audit_logs** | Security audit trail | action, user, timestamp |
| **environments** | Environment configs | name, variables, secrets |

### Key Schema Patterns

#### User Document
```json
{
  "_id": "ObjectId",
  "username": "john.doe",
  "email": "john@company.com",
  "role": "developer",
  "permissions": ["create_app", "deploy", "rollback"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Application Document
```json
{
  "_id": "ObjectId",
  "name": "payment-service",
  "status": "active",
  "environments": {
    "production": {
      "url": "https://api.example.com",
      "version": "v2.1.3",
      "health_status": "healthy"
    }
  },
  "metadata": {
    "total_deployments": 247,
    "uptime_percentage": 99.95
  }
}
```

#### Deployment Document
```json
{
  "_id": "ObjectId",
  "application_id": "ObjectId",
  "version": "v2.1.4",
  "status": "success",
  "environment": "production",
  "deployed_by": "john.doe",
  "metrics": {
    "deployment_duration": 180,
    "success_rate": 98.5
  },
  "created_at": "2024-01-16T14:22:00Z"
}
```

---

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "New User",
  "role": "developer"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@capx.io",
  "password": "Admin@123"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "...",
    "role": "admin",
    "permissions": [...]
  }
}
```

### Application Endpoints

#### List Applications
```http
GET /api/applications
Authorization: Bearer {token}
```

#### Create Application
```http
POST /api/applications
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "my-service",
  "description": "My microservice",
  "repository_url": "https://github.com/org/repo",
  "language": "python",
  "framework": "flask"
}
```

### Deployment Endpoints

#### Create Deployment
```http
POST /api/deployments
Authorization: Bearer {token}
Content-Type: application/json

{
  "application_id": "...",
  "application_name": "my-service",
  "version": "v1.2.0",
  "environment": "production",
  "commit_hash": "abc123",
  "docker_image": "myregistry/my-service:v1.2.0"
}
```

#### Get Deployment History
```http
GET /api/deployments?limit=20
Authorization: Bearer {token}
```

### Dashboard Endpoints

#### Get Dashboard Stats
```http
GET /api/dashboard/stats
Authorization: Bearer {token}

Response:
{
  "overview": {
    "total_applications": 42,
    "total_deployments": 1247,
    "open_incidents": 3
  },
  "deployments": {
    "success_rate": 98.5,
    "total": 1247
  },
  "incidents": {
    "critical": 1,
    "avg_mttr_minutes": 12.5
  }
}
```

---

## 🚢 Deployment

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace capx-platform

# Create secrets
kubectl create secret generic capx-secrets \
  --from-literal=MONGO_URI="your-mongo-uri" \
  --from-literal=SECRET_KEY="your-jwt-secret" \
  --namespace=capx-platform

# Deploy backend
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml

# Deploy frontend
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

# Check status
kubectl get pods -n capx-platform
kubectl get services -n capx-platform
```

### AWS Deployment

```bash
# Configure AWS CLI
aws configure

# Apply Terraform
cd infrastructure/terraform
terraform init
terraform apply

# Configure kubectl for EKS
aws eks update-kubeconfig --name capx-cluster --region us-east-1

# Deploy application
kubectl apply -f ../kubernetes/
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

Access Prometheus at `http://localhost:9090`

Key metrics:
- `capx_deployment_total` - Total deployments
- `capx_deployment_success_rate` - Deployment success rate
- `capx_incident_count` - Number of incidents
- `capx_app_health_status` - Application health

### Grafana Dashboards

Access Grafana at `http://localhost:3001`

Pre-configured dashboards:
1. **Platform Overview** - System-wide metrics
2. **Application Health** - Per-app health status
3. **Deployment Analytics** - Deployment trends
4. **Incident Response** - MTTR and resolution times

### ELK Stack

Access Kibana at `http://localhost:5601`

Features:
- Full-text log search
- Log aggregation by application
- Custom dashboards
- Alert rules

---

## 🤖 Auto-Healing

### How It Works

1. **Detection**: Background service monitors applications every 60 seconds
2. **Analysis**: Checks for common issues (crash loops, high memory, etc.)
3. **Incident Creation**: Creates incident record in MongoDB
4. **Remediation**: Applies appropriate fix strategy
5. **Verification**: Confirms issue resolution
6. **Logging**: Records entire timeline

### Supported Auto-Healing Scenarios

| Issue | Detection | Remediation |
|-------|-----------|-------------|
| Pod Crash Loop | Restart count > 3 | Rollback or restart |
| High Memory | Memory > 90% | Restart high-memory pods |
| High CPU | CPU > 90% | Scale up replicas |
| Pod Not Ready | Ready < Desired | Restart deployment |
| Service Unavailable | Health check fails | Refresh service endpoints |

### Run Auto-Healing Engine

```bash
# Standalone
cd auto-healing
python auto_remediation.py

# Kubernetes Deployment
kubectl apply -f infrastructure/kubernetes/auto-healing-deployment.yaml
```

---

## 🔐 Security

### Authentication Flow

1. User submits credentials
2. Backend validates against MongoDB
3. JWT token generated (24-hour expiry)
4. Token included in all subsequent requests
5. Middleware validates token on each request

### RBAC Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | All permissions, user management |
| **Developer** | Create apps, deploy, trigger pipelines |
| **Viewer** | Read-only access to metrics and logs |

### Security Best Practices

- ✅ JWT tokens with short expiry
- ✅ Passwords hashed with Werkzeug
- ✅ HTTPS in production (configure ingress)
- ✅ Secrets in Kubernetes secrets or AWS Secrets Manager
- ✅ Network policies in Kubernetes
- ✅ AWS IAM roles for service accounts
- ✅ Audit logging for all actions

---

## 🎓 Interview Guide

### System Design Questions

**Q: How does the platform handle high availability?**

A: The platform uses Kubernetes for orchestration with horizontal pod autoscaling (HPA) that scales from 3 to 10 replicas based on CPU/memory usage. We use health checks and readiness probes to ensure traffic only goes to healthy pods. MongoDB can be configured with replica sets for high availability. AWS EKS provides multi-AZ deployment.

**Q: Explain the deployment pipeline.**

A: We use GitOps with GitHub Actions. When code is pushed, the CI pipeline runs tests and builds Docker images, pushes to ECR, and triggers Kubernetes deployment. The deployment service in our backend tracks this in MongoDB, allowing us to view history, success rates, and trigger rollbacks. We support rolling, blue-green, and canary strategies.

**Q: How does auto-healing work?**

A: We run a Python service that checks application health every 60 seconds. It detects issues like crash loops, high resource usage, and pod readiness. When detected, it creates an incident in MongoDB and applies remediation strategies like pod restarts, scaling, or rollbacks. The entire timeline is recorded for analysis.

### Technical Deep Dives

**Database Design**:
- Why MongoDB? Schema flexibility, easy scaling, native JSON
- Collections mirror domain entities (users, apps, deployments)
- Indexes on frequently queried fields (email, status, timestamps)
- Aggregation pipelines for statistics

**API Architecture**:
- RESTful design with resource-based URLs
- JWT middleware for authentication
- CORS enabled for frontend communication
- Proper HTTP status codes and error handling

**Frontend Architecture**:
- React with Vite for fast builds
- Tailwind for utility-first styling
- Framer Motion for animations
- Component-based architecture
- Custom hooks for API calls

---

## 🔧 Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check MongoDB connection
mongosh "your-connection-string"

# Verify Python version
python --version  # Should be 3.11+

# Check logs
python app.py  # Run in foreground to see errors
```

**Frontend build fails**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

**Kubernetes pods stuck in Pending**
```bash
# Check events
kubectl describe pod <pod-name> -n capx-platform

# Check resources
kubectl top nodes

# Check secrets
kubectl get secrets -n capx-platform
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Inspired by:
- Google's Borg and Kubernetes
- Netflix's Spinnaker
- Amazon's Internal DevOps Tools
- Backstage by Spotify

---

## 📬 Contact

**Project Maintainer**: Ayush Raj

- 📧 **Email:** rajayush9052@gmail.com
- 💼 **LinkedIn:** [Ayush Raj](https://www.linkedin.com/in/ayush-raj-a11b82219/)
- 🌐 **GitHub:** [@ayu9x](https://github.com/ayu9x)


---

<div align="center">

**Built with ❤️ for Platform Engineering**

[⬆ Back to Top](#-cap-x-cloud-autonomous-platform)

</div>