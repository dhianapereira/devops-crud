variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
}

variable "ssh_key_name" {
  description = "Name of an existing SSH key in DigitalOcean"
  type        = string
  default     = "github-actions"
}
