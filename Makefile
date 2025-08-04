.PHONY: dev test deploy install clean local

dev: fix
	@. .venv/bin/activate && export PYTHONPATH=$$(pwd):$$PYTHONPATH && . .env && TEST=True python -m Program

heavy: fix
	@. .venv/bin/activate && export PYTHONPATH=$$(pwd):$$PYTHONPATH && . .env && python -m Program

fix:
	@. .venv/bin/activate && isort .
	@. .venv/bin/activate && black .
	#@nfmt .

install: clean
	@python3 -m venv .venv
	@. .venv/bin/activate && pip install -r requirements.txt
	@. .venv/bin/activate && pip install isort git+https://github.com/pre63/black.git

clean:
	@rm -rf .venv | true
	@rm -rf __pycache__ | true
	@rm -rf .pytest_cache | true
	@rm -rf .mypy | true