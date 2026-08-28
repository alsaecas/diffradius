.PHONY: test validate evaluate

test:
	pytest

validate:
	python scripts/validate_benchmark.py

evaluate:
	diffradius evaluate --mode both --output results/benchmark
