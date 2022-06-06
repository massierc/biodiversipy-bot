# Biodiversipy Bot

[biodiversipy](https://github.com/TmtStss/biodiversipy)'s Telegram bot.

Create a gcloud function:

```sh
gcloud functions deploy biodiversipy_bot --set-env-vars "TELEGRAM_TOKEN=<TELEGRAM_TOKEN>" --runtime python38 --trigger-http --project=le-wagon-bootcamp-346910
```

Set up webhook:

```sh
curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<URL>"
```
