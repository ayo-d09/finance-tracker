terraform {
    backend "s3" {
        bucket = "finance-tracker-terraform-state"
        key    = "terraform.tfstate"
        region = "us-east-1"
        dynamodb_table = "finance-tracker-terraform-lock"
        encrypt = true
    }
}