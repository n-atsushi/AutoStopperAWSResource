#tfsec:ignore:aws-ec2-require-vpc-flow-logs-for-all-vpcs
resource "aws_vpc" "auto-stop-vpc" {
  cidr_block = var.vpc.vpc_cidr_block

  tags = {
    Name = var.vpc.vpc_name
  }
}
