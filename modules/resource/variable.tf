variable "lambdas" {
  type = map(object({
    lambda_name = string
    role = object({
      role_name = string
    })
  }))
}