#tfsec:ignore:aws-ec2-require-vpc-flow-logs-for-all-vpcs
resource "aws_vpc" "auto-stop-vpc" {
  cidr_block = "192.168.0.0/16"
  tags = {
    Name = var.vpc.vpc_name
  }
  
}
