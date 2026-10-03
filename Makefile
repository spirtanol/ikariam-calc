DC = docker compose
FILE ?= example.yml

.PHONY: shell cost battle

shell:
	$(DC) run --rm -it cli bash

cost:
	$(DC) run --rm -T cli poetry run python -m app cost $(FILE) $(if $(OUT),--output $(OUT))

battle:
	$(DC) run --rm -T cli poetry run python -m app battle $(FILE) $(if $(OUT),--output $(OUT))