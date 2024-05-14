
variable "vpc" {
  type = object({
    vpc_name = string
  })
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "subnets" {
  type = map(object({
    subnet_name = string
  }))
}