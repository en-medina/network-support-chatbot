variable "gns3_allowed_ip" {
  description = "The IP address allowed to access the GNS3 server (for SSH and web UI). Use CIDR notation, e.g., '203.0.113.0/24'"
  type        = string
  default     = "0.0.0.0/0"
}