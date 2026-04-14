terraform {
    backend "s3" {
        bucket = "finance-tracker-tfstate-243768737939"
        key    = "terraform.tfstate"
        region = "us-east-1"
        dynamodb_table = "terraform-state-lock"
        encrypt = true
    }
}