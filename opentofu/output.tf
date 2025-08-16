
output "receiver_function_name" {
  value = module.receiver_function.function_name
}

output "api_gateway_endpoint" {
  value = module.api_gateway.invoke_url
}

output "telegram_webhook_url" {
  value = "${module.api_gateway.invoke_url}/telegram"
}

output "webhook_secret" {
  value = random_string.webhook_secret.result
}

output "ecr_repository_url" {
  value = {
    generator = aws_ecr_repository.generator.repository_url
    receiver  = aws_ecr_repository.receiver.repository_url
  }
}