up:
	docker compose up -d

build:
	docker compose build

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

clean:
	docker system prune -f

bash:
	docker compose exec resumaster_bot bash
