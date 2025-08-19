set webhook:

```sh
curl --location https://api.telegram.org/bot{TELEGRAM_API}/setWebhook \
--form 'url="{URL}"' \
--form 'secret_token="{TOKEN}"'
```

curl -X POST https://api.telegram.org/bot{TELEGRAM_KEY}/getWebhookInfo

sample request:

```json
{
	"update_id": 696452904,
	"message": {
		"message_id": 2,
		"from": {
			"id": 746906594,
			"is_bot": false,
			"first_name": "Enmanuel",
			"last_name": "Medina",
			"language_code": "en"
		},
		"chat": {
			"id": 746906594,
			"first_name": "Enmanuel",
			"last_name": "Medina",
			"type": "private"
		},
		"date": 1755095252,
		"text": "Hi"
	}
}
```
