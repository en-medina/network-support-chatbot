
resource "aws_ssm_parameter" "main" {
  for_each = toset(local.parameters)
  name  = "/chatbot/${each.value}"
  type  = "SecureString"
  value = "placeholder"

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
