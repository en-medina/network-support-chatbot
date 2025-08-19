
module "api_gateway_account_settings" {
  source  = "cloudposse/api-gateway/aws//modules/account-settings"
  version = "0.9.0"

}

module "api_gateway" {
  source  = "cloudposse/api-gateway/aws"
  version = "0.9.0"

  name          = "network-support-api"
  endpoint_type = "REGIONAL"
  stage_name    = "prod"

  openapi_config = {
    openapi = "3.0.1"
    info = {
      title   = "api"
      version = "1.0"
    }
    paths = {
      "/telegram" = {
        post = {
          responses = {
            "200" = {
              description = "Successful response"
              content     = {}
            }
            "400" = {
              description = "Bad request"
              content     = {}
            }
          }
          x-amazon-apigateway-integration = {
            type       = "aws_proxy"
            httpMethod = "POST"

            uri                  = "${module.receiver_function.invoke_arn}"
            passthrough_behavior = "when_no_match"
            response = {
              default = {
                statusCode = "200"
              }
            }
          }
        }
      }
    }
  }
  depends_on = [module.api_gateway_account_settings]
}

# Create Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.receiver_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${module.api_gateway.execution_arn}/*/*"
}