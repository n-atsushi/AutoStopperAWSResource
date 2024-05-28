variable "lambdas" {
  type = map(object({
    lambda_name = string
    role = object({
      role_name = string
      policies = object({
        ec2 = object({
          actions = list(string)
          resources = list(string)
        })
        s3 = object({
          actions = list(string)
          s3_resource = string
        })
      })
    })
    ecr = object({
      ecr_name = string
    })
  }))
}

variable "s3" {
  type = map(object({
    bucket_name = string
  }))
}
