resource "random_string" "webhook_secret" {
  length  = 20
  special = false
  upper   = true
  lower   = true
  numeric = true
}

module "receiver_function" {
  source  = "cloudposse/lambda-function/aws"
  version = "0.6.1"

  function_name = "message-receiver"
  description   = "Lambda function to receive messages from API Gateway and send to SQS"
  package_type	 = "Image"
  image_uri     = "${aws_ecr_repository.receiver.repository_url}:latest"

  inline_iam_policy = data.aws_iam_policy_document.receiver.json

  timeout     = 10  # Timeout in seconds
  memory_size = 128 # Memory size in MB

  lambda_environment = {
    variables = {
      SQS_QUEUE_URL = aws_sqs_queue.main.url
      WEBHOOK_TOKEN = random_string.webhook_secret.result
      ENVIRONMENT   = "production"
    }
  }
}

module "generator_function" {
  source  = "cloudposse/lambda-function/aws"
  version = "0.6.1"

  function_name = "message-generator"
  description   = "Lambda function to receive messages from API Gateway and send to SQS"
  package_type	 = "Image"
  image_uri     = "${aws_ecr_repository.generator.repository_url}:latest"

  inline_iam_policy = data.aws_iam_policy_document.generator.json

  timeout     = 5 * 60 # Timeout in seconds
  memory_size = 256    # Memory size in MB

  lambda_environment = {
    variables = {
      ENVIRONMENT = "production"
    }
  }
}
