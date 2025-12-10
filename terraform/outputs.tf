output "droplet_ip" {
  description = "Public IP address of the droplet"
  value       = digitalocean_droplet.app.ipv4_address
}
