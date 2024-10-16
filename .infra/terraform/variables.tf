variable "instance_type" {
  default = "t2.micro"
}

variable "key_name" {
  description = "SSH key name"
  default     = "my-ssh-key"
}

variable "subnet_id" {
  description = "Subnet ID where the instance will be created"
  default     = ""
}
