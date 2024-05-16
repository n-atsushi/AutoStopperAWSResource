

resource "aws_subnet" "subnets" {
  for_each = var.subnets

  vpc_id     = aws_vpc.auto-stop-vpc.id
  cidr_block = each.value.cidr_block

  tags = {
    Name = each.value.subnet_name
  }
}