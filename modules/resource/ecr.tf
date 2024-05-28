resource "aws_ecr_repository" "ecr" {
  for_each = var.lambdas

  name                 = "${each.value.ecr.ecr_name}-repository"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
