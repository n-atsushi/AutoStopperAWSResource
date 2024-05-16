terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "terraform-state-list-atsushi"
    region = "ap-northeast-1"
    key    = "dev/terraform.tfstate"
  }
}

provider "aws" {
  region = "ap-northeast-1"
  default_tags {
    tags = {
      env = "dev"
    }
  }
}

# create networks
module "dev-networks" {
  source = "../../modules/networks"

  vpc = {
    vpc_name = "AutoStopVPC"
  }

  subnets = {
    az-1a-subnet = {
      subnet_name = "az-1a-subnet"
      cidr_block  = "192.168.1.0/24"
    }
    az-1c-subnet = {
      subnet_name = "az-1c-subnet"
      cidr_block  = "192.168.2.0/24"
    }
  }
}

module "dev-resources" {
  source = "../../modules/resource"

  lambdas = {
    auto-stop-lamda = {
      lambda_name = "auto-stop-lambda"
      role = {
        role_name = "auto-stop-lamnda-role"
      }
    } 
  }

}