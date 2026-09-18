.PHONY: test results figures paper paper-draft reproduce style

test:
	python -m pytest -q

results:
	python experiments/run_all.py
	python experiments/additional_checks.py

figures:
	python experiments/make_figures.py

style:
	python scripts/fetch_style.py

paper: style figures
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex

paper-draft: figures
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex

reproduce:
	python scripts/check_reproduction.py
