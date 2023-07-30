dev:
	docker-compose up -d
	REEL_MONGODB_CONNECTION_STRING=mongodb://localhost:27017/?directConnection=true \
	REEL_MONGODB_DATABASE_NAME=reel \
	poetry run uvicorn reel.main:app --reload
