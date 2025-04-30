terraform {
  required_version = ">=1.4.0"
  required_providers { aws = { source = "hashicorp/aws"  version = "~>5.0" } }
}

provider "aws" { region = var.region }

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  name    = "ai-trading-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["${var.region}a", "${var.region}b"]
  public_subnets  = ["10.0.1.0/24","10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24","10.0.102.0/24"]
}

resource "aws_secretsmanager_secret" "schwab" { name = "schwab-creds" }

module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws"
  name    = "ai-trading-cluster"
  vpc_id  = module.vpc.vpc_id
  subnets = module.vpc.private_subnets
}

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  identifier = "aitrading"
  engine     = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  db_name           = "aitrading"
  username          = var.db_user
  password          = var.db_pass
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  subnet_ids              = module.vpc.private_subnets
}
