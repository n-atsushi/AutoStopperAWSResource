
resource "aws_s3_bucket" "s3" {
  for_each = var.s3

  bucket = each.value.bucket_name
}
