terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34.1"
    }
  }

  backend "remote" {
    organization = "devops-crud-organization"

    workspaces {
      name = "devops-crud"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

data "digitalocean_ssh_key" "existing" {
  name = var.ssh_key_name
}

resource "digitalocean_droplet" "app" {
  name   = "devops-crud-droplet"
  region = "nyc1"
  size   = "s-1vcpu-1gb"
  image  = "ubuntu-24-04-x64"

  ssh_keys = [data.digitalocean_ssh_key.existing.id]

  user_data = file("${path.module}/cloud-init.yml")

  tags = ["devops", "crud", "ci-cd"]

  lifecycle {
    prevent_destroy = false
  }
}
