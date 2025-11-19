# General
define set-default-container
	ifndef c
	c = api
	else ifeq (${c},all)
	override c=
	endif
endef

set-container:
	$(eval $(call set-default-container))

build:
	docker compose -f docker-compose.dev.yml build
up:
	docker compose -f docker-compose.dev.yml up -d
down:
	docker compose -f docker-compose.dev.yml down
restart: set-container
	docker compose -f docker-compose.dev.yml restart $(c)
exec: set-container
	docker compose -f docker-compose.dev.yml exec $(c) /bin/bash
startup: build up

migrate: set-container
	docker compose -f docker-compose.dev.yml exec $(c) alembic upgrade head