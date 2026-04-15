variable "app_name" {
  description = "The name of the application"
  type        = string
}

variable "security_group_id" {
  description = "The security group ID for the ALB"
  type        = string
}

variable "subnet_ids" {
  description = "The subnet IDs for the ALB"
  type        = list(string)
}

variable "vpc_id" {
  description = "The VPC ID for the ALB"
  type        = string
}
