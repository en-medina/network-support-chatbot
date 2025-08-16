terraform {
  required_version = "~> 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1" # Change to your preferred region
  default_tags {
    tags = {
      Environment = "viu-project"
      Project     = "network-support-chatbot"
    }
  }
}

# Optional: Configure remote state if needed
terraform {
  backend "s3" {
    bucket = "viu-project-tf-state-as3dcgnsxs"
    key    = "network-support-chatbot/terraform.tfstate"
    region = "us-east-1"
  }
}