resource "aws_sqs_queue" "main" {
  name                       = "network-support-queue"
  visibility_timeout_seconds = 10 * 60 # 10 minutes
  message_retention_seconds  = 86400 # 1 day

  tags = {
    Name = "network-support-chatbot"
  }
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.main.arn
  function_name    = module.generator_function.function_name
  batch_size       = 1 # Number of messages to process in one batch

  scaling_config {
    maximum_concurrency = 5
  }
}

resource "aws_lambda_permission" "allow_sqs_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = module.generator_function.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.main.arn
}
