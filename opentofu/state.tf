resource "aws_s3_bucket" "state" {
  bucket = "viu-project-tf-state-as3dcgnsxs"

  lifecycle {
    prevent_destroy = true
  }
}
