# Finance Tracker

A containerised Python API deployed on AWS ECS Fargate with Terraform.


## Stack

- FastAPI (Python)
- AWS ECS Fargate
- AWS RDS (Postgresql)
- Terraform
- GitHub Actions


## Project Structure

- `app/` — FastAPI application and Dockerfile
- `infra/` — Terraform modules for networking, RDS, and ECS
- `scripts/` — deploy and destroy scripts


## Concepts

**Containerisation** — Dockerfile, building an image, running an app in a container

**CI/CD** — Automated build, push, and deploy on every commit using OIDC instead of hardcoded credentials

**Infrastructure as Code** — Cloud resources defined in Terraform modules with remote state management

**Networking** — VPC, public/private subnets, security groups. RDS sits in private subnets with no internet access

**IAM / Least Privilege** — Task execution role scoped to only what ECS needs, no over-permissioned roles

**Managed Services** — ECS Fargate runs containers without managing servers, RDS manages the database


## Deploy

1. Create S3 bucket and DynamoDB table for Terraform state
2. Add `AWS_ROLE_ARN` to GitHub secrets
3. Push to main — pipeline handles the rest


## Destroy

```bash
bash scripts/destroy.sh
```