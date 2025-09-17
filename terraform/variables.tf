variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "chessaroo-tf"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "container_port" {
  description = "Port exposed by the docker image to redirect traffic to"
  type        = number
  default     = 3000
}

variable "ecs_cpu" {
  description = "Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  type        = string
  default     = "256"
}

variable "ecs_memory" {
  description = "Fargate instance memory to provision (in MiB)"
  type        = string
  default     = "512"
}

variable "ecs_desired_count" {
  description = "Number of docker containers to run"
  type        = number
  default     = 2
}

