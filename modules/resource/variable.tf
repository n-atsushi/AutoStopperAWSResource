variable "lambdas" {
  type = map(object({
    lambda_name = string
    role = object({
      role_name = string
    })
  }))
}

variable "s3" {
  type = map(object({
    bucket_name = string
  }))
}
