locals {
  inline_policeis = {
    "cloudwatch-policy" = data.aws_iam_policy_document.aws_iam_policy_document_cloudwatch.json
    #"ec2-policy" = data.aws_iam_policy_document.aws_iam_policy_document_ec2.json,
    #"s3-policy" = data.aws_iam_policy_document.aws_iam_policy_document_s3.json,
  }
}

data "aws_iam_policy_document" "lambda_assume_role" {

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "aws_iam_policy_document_cloudwatch" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

data "aws_iam_policy_document" "aws_iam_policy_document_ec2" {
  statement {
    sid = "auto-stop-EC2"

    actions = ["ec2:*"]

    resources = [
      "arn:aws:s3:::somebucket",
      "arn:aws:s3:::somebucket/*",
    ]
  }
}

data "aws_iam_policy_document" "aws_iam_policy_document_s3" {
  statement {
    sid = "auto-stop-S3"

    actions = ["s3:*"]

    resources = [
      "arn:aws:s3:::somebucked",
      "arn:aws:s3:::somebucked/*",
    ]
  }
}

resource "aws_iam_role" "lambda_role" {
  for_each = var.lambdas

  name               = each.value.role.role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  dynamic "inline_policy" {
    for_each = local.inline_policeis

    content {
      name = inline_policy.key 
      policy = inline_policy.value
    }
  }
}

# data "archive_file" "lambda_scripts" {
#   type        = "zip"
#   source_file = "lambda_scripts.js"
#   output_path = "lambda_function_payload.zip"
# }

# resource "aws_lambda_function" "test_lambda" {
#   filename      = "lambda_function_payload.zip"
#   function_name = "lambda_function_name"
#   role          = aws_iam_role.iam_for_lambda.arn
#   handler       = "index.test"

#   source_code_hash = data.archive_file.lambda_scripts.output_base64sha256

#   runtime = "nodejs18.x"

#   environment {
#     variables = {
#       foo = "bar"
#     }
#   }
# }
