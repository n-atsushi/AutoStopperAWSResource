locals {
  inline_polices = {
    auto-stop-lambda = {
      "cloudwatch-policy" = data.aws_iam_policy_document.aws_iam_policy_document_cloudwatch.json
      "ec2-policy" = data.aws_iam_policy_document.aws_iam_policy_document_ec2["auto-stop-lambda"].json,
      "s3-policy" = data.aws_iam_policy_document.aws_iam_policy_document_s3["auto-stop-lambda"].json,
    }
    auto-stop-db-lambda = {
      "cloudwatch-policy" = data.aws_iam_policy_document.aws_iam_policy_document_cloudwatch.json
      "s3-policy" = data.aws_iam_policy_document.aws_iam_policy_document_s3["auto-stop-db-lambda"].json,
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
    effect  = "Allow"
    actions = each.value.role.policies.s3.actions

    resources = flatten([
      aws_s3_bucket.s3[each.value.role.policies.s3.s3_resource].arn,
      "${aws_s3_bucket.s3[each.value.role.policies.s3.s3_resource].arn}/*",
      each.key == "auto-stop-db-lambda" ? [
        aws_s3_bucket.s3["s3-auto-resource"].arn,
        "${aws_s3_bucket.s3["s3-auto-resource"].arn}/*",
      ] : []
    ])
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
  architectures = ["arm64"]

  environment {
    variables = {
      "REGION_NAME": "ap-northeast-1",
      "S3_AUTO_RESOURCE_DB_BUCKET": "s3-auto-resource-db-atsushi",
      "S3_AUTO_RESOURCE_DB_PATH": "db-resources",
      "S3_AUTO_RESOURCE_DB_OBJ": "aws_resources.db",
      "S3_AUTO_RESOURCE_YML_BUCKET": "s3-auto-resource-yml-atsushi"
    }
  }
}

# # ymlのトリガー
# resource "aws_s3_bucket_notification" "bucket_notification_yml" {
#   bucket = aws_s3_bucket.s3["s3-auto-resource"].id
#
#   lambda_function {
#     lambda_function_arn = aws_lambda_function.lambda[auto-stop-db-lambda].arn
#     events              = ["s3:ObjectCreated:*"]
#     filter_prefix       = "AWSLogs/"
#     filter_suffix       = ".log"
#   }
#
#   depends_on = [aws_lambda_permission.allow_bucket_yml]
# }
#
# resource "aws_lambda_permission" "allow_bucket_yml" {
#   statement_id  = "AllowExecutionFromS3Bucket"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.lambda[auto-stop-db-lambda].function_name
#   principal     = "s3.amazonaws.com"
#   source_arn    = aws_s3_bucket.s3["s3-auto-resource"].arn
# }
