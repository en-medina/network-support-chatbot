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
  statement {
    sid    = "BedrockInvoke"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
      "bedrock:InvokeModelWithResponse"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "bedrock" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.model.arn,
      "${aws_s3_bucket.model.arn}/*",
    ]
  }
}

module "bedrock_role" {
  source  = "cloudposse/iam-role/aws"
  version = "0.22.0"

  name = "bedrock-role"

  policy_description = "Policy for Bedrock to access S3 and other resources"
  role_description   = "Role for Bedrock to access S3 and other resources"

  principals = {
    Service = ["bedrock.amazonaws.com"]
  }

  policy_documents = [
    data.aws_iam_policy_document.bedrock.json
  ]
}
