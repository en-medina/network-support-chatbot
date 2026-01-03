data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-20250821"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}