data "aws_iam_policy_document" "receiver" {
  statement {
    sid       = "SQSAccess"
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.main.arn]
  }
}

data "aws_iam_policy_document" "generator" {
  statement {
    sid    = "SQSAccess"
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
    resources = [aws_sqs_queue.main.arn]
  }
  statement {
    sid    = "SSMAccess"
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
    ]
    resources = ["*"]
  }
}