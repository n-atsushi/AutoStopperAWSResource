resource "aws_ecr_repository" "ecr" {
  for_each = var.ecr

  name                 = each.value.ecr_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
