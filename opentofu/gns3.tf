# Security group for GNS3 instance
resource "aws_security_group" "gns3_sg" {
  name        = "gns3-security-group"
  description = "Security group for GNS3 server"

  # GNS3 web UI
  ingress {
    from_port   = 3080
    to_port     = 3080
    protocol    = "tcp"
    cidr_blocks = [var.gns3_allowed_ip]
  }

  # GNS3 web UI
  ingress {
    from_port   = 5000
    to_port     = 5100
    protocol    = "tcp"
    cidr_blocks = [var.gns3_allowed_ip]
  }


  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "gns3_server" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t3.medium" # Minimum recommended for GNS3
  security_groups      = [aws_security_group.gns3_sg.name]
  iam_instance_profile = module.ec2_role.instance_profile

  # User data to install GNS3
  user_data = <<-EOF
        #!/bin/bash
        # Enable IP forwarding
        sudo sysctl -w net.ipv4.ip_forward=1
        echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

        # Set up NAT using iptables
        sudo iptables -t nat -A POSTROUTING -o ens5 -j MASQUERADE

        cd /tmp
        curl https://raw.githubusercontent.com/GNS3/gns3-server/master/scripts/remote-install.sh > gns3-remote-install.sh
        bash gns3-remote-install.sh --with-iou --with-i386-repository
    EOF

  root_block_device {
    volume_size = 64 # GiB, increase based on your needs
    volume_type = "gp3"
  }

  tags = {
    Name = "GNS3-Server"
  }
}

# Output the public IP of the instance
