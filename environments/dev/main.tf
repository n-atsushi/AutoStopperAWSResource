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
    }
    az-1c-subnet = {
      subnet_name = "az-1c-subnet"
    }
  }
}