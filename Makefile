dev:
	docker-compose up -d
	MONGODB_CONNECTION_STRING=mongodb://localhost:27017/?directConnection=true \
	MONGODB_DATABASE_NAME=reel \
	poetry run uvicorn reel.main:app --reload
