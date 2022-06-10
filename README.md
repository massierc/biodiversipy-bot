# Biodiversipy Bot

[biodiversipy](https://github.com/TmtStss/biodiversipy)'s Telegram bot.

## Run your own instance

Create a gcloud function:

```sh
gcloud functions deploy <bot_name> --set-env-vars "TELEGRAM_TOKEN=<TELEGRAM_TOKEN>" --runtime python38 --trigger-http --project=<gcloud_project_id> --region=<region>
```

Set up webhook:

```sh
curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<URL>"
```
