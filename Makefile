deploy:
	@gcloud functions deploy telegram_bot_v2 \
		--project=le-wagon-bootcamp-346910 \
		--trigger-http \
		--runtime=python38 \
		--region=europe-west1
