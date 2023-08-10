# Makefile

format-black:
	@black .

format-isort:
	@isort .

lint-black:
	@black . --check

lint-isort:
	@isort . --check

lint-bandit:
	@bandit .

lint-flake8:
	@flake8 .

format: format-black format-isort

lint: lint-black lint-isort lint-bandit lint-flake8
