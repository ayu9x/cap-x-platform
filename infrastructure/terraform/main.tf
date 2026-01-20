# Terraform Configuration for CAP-X Platform on AWS

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }
  
  backend "s3" {
    bucket         = "capx-terraform-state"
    key            = "capx/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "capx-terraform-locks"
  }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "CAP-X"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Kubernetes Provider Configuration
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name
    ]
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr             = var.vpc_cidr
  environment          = var.environment
  availability_zones   = data.aws_availability_zones.available.names
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

# EKS Module
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = "${var.project_name}-${var.environment}"
  cluster_version = var.eks_cluster_version
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  
  node_groups = {
    general = {
      desired_size = var.eks_node_desired_size
      min_size     = var.eks_node_min_size
      max_size     = var.eks_node_max_size
      instance_types = var.eks_node_instance_types
    }
  }
}

# RDS Module
module "rds" {
  source = "./modules/rds"
  
  identifier          = "${var.project_name}-${var.environment}-db"
  engine              = "postgres"
  engine_version      = "15.3"
  instance_class      = var.rds_instance_class
  allocated_storage   = var.rds_allocated_storage
  db_name             = var.db_name
  username            = var.db_username
  password            = var.db_password
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  multi_az            = var.environment == "production" ? true : false
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  bucket_name = "${var.project_name}-${var.environment}-storage"
  environment = var.environment
  
  versioning_enabled = var.environment == "production" ? true : false
  lifecycle_rules    = var.s3_lifecycle_rules
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-${var.environment}-redis-subnet"
  subnet_ids = module.vpc.private_subnet_ids
}

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Security group for Redis cluster"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-${var.environment}-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis.id]
}