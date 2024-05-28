locals {
  inline_polices = {
    auto-stop-lambda = {
      "cloudwatch-policy" = data.aws_iam_policy_document.aws_iam_policy_document_cloudwatch.json
      "ec2-policy" = data.aws_iam_policy_document.aws_iam_policy_document_ec2["auto-stop-lambda"].json,
      "s3-policy" = data.aws_iam_policy_document.aws_iam_policy_document_s3["auto-stop-lambda"].json,
    }
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
  for_each = var.lambdas

  statement {
    effect = "Allow"

    actions = each.value.role.policies.ec2.actions

    resources = each.value.role.policies.ec2.resources
  }
}

data "aws_iam_policy_document" "aws_iam_policy_document_s3" {
  for_each = var.lambdas

  statement {
    effect = "Allow"
    actions = each.value.role.policies.s3.actions

    resources = [
      aws_s3_bucket.s3[each.value.role.policies.s3.s3_resource].arn,
      "${aws_s3_bucket.s3[each.value.role.policies.s3.s3_resource].arn}/*"
    ]
  }
}

resource "aws_iam_role" "lambda_role" {
  for_each = var.lambdas

  name               = each.value.role.role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  dynamic "inline_policy" {
    for_each = local.inline_polices[each.key]

    content {
      name = inline_policy.key
      policy = inline_policy.value
    }
  }
}


resource "aws_lambda_function" "lambda" {
  for_each = var.lambdas

  function_name = each.value.lambda_name
  role          = aws_iam_role.lambda_role[each.key].arn
  package_type = "Image"
  image_uri = "${aws_ecr_repository.ecr[each.key].repository_url}:latest"
  memory_size = 128
  timeout = 60

  environment {
    variables = {
      foo = "bar"
    }
  }
}
