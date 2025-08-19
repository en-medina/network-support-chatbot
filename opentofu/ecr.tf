
resource "aws_ecr_repository" "generator" {
  name = "generator-function"
}

resource "aws_ecr_repository" "receiver" {
  name = "receiver-function"
}

resource "aws_ecr_lifecycle_policy" "main" {
  for_each = {
    "generator" = aws_ecr_repository.generator
    "receiver"  = aws_ecr_repository.receiver
  }
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
