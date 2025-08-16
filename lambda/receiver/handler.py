import json
import os
import boto3

def handler(event, context):
    """
    AWS Lambda function that reads JSON body from API Gateway request.
    """
    webhook_token = os.environ.get('WEBHOOK_TOKEN', None)
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if webhook_token:
        received_token = headers.get("x-telegram-bot-api-secret-token", "")
        if received_token != webhook_token:
            print(f"Forbidden: Invalid token")
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "Forbidden"})
            }
    print("Message received from Telegram")
    # API Gateway sends body as a JSON string
    payload = json.loads(event.get("body", "{}"))

    if not payload:
        print("No payload found in the request body")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid payload"})
        }
    if "message" not in payload:
        print("No message found in the payload")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No message found in payload"})
        }

    sqs = boto3.client('sqs')
    sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
    # Process the JSON body as needed
    telegram_message = {
        "type": "telegram",
        "message": payload
    }

    # Send message to SQS
    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=json.dumps(telegram_message)
    )
    print("Message sent to SQS queue")

    return {
        "statusCode": 200,
        "body":  json.dumps({"message": "Message processed successfully"})
    }
