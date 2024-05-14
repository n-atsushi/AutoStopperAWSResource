resource "aws_subnet" "az-1a-subnet" {
  vpc_id     = aws_vpc.auto-stop-vpc.id
  cidr_block = cidrsubnet(aws_vpc.auto-stop-vpc.cidr_block, 8, 1)
  
  tags = {
    Name = var.subnets.az-1a-subnet.subnet_name
  }
}

resource "aws_subnet" "az-1c-subnet" {
  vpc_id     = aws_vpc.auto-stop-vpc.id
  cidr_block = cidrsubnet(aws_vpc.auto-stop-vpc.cidr_block, 8, 2)

  tags = {
    Name = var.subnets.az-1c-subnet.subnet_name
  }
}
