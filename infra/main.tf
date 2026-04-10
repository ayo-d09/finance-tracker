provider "aws" {
  region = var.region
}

module "networking" {
  source   = "./modules/networking"
  app_name = var.app_name
}

module "rds" {
  source                = "./modules/rds"
  app_name              = var.app_name
  db_password           = var.db_password
  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.private_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id  
}

module "ecs" {
  source           = "./modules/ecs"
  app_name         = var.app_name
  vpc_id           = module.networking.vpc_id
  subnet_ids       = module.networking.private_subnet_ids
  db_endpoint      = module.rds.db_endpoint
  container_image  = var.container_image
  ecs_security_group_id = module.networking.ecs_security_group_id
}