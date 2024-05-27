
variable "vpc" {
  type = object({
    vpc_name = string
    vpc_cidr_block = string
  })
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "subnets" {
  type = map(object({
    subnet_name = string
    cidr_block  = string
  }))
}
