variable region { 
    description = "AWS region to deploy resources in"
    default     = "us-east-1"
}

variable app_name {
    description = "Name of the application"
    default     = "finance-tracker"
}

variable db_password {
    description = "Password for the RDS database"
    sensitive   = true
}

variable "container_image" {
  description = "The Docker image to deploy in ECS"
  default = "243768737939.dkr.ecr.us-east-1.amazonaws.com/finance-tracker:latest"
}