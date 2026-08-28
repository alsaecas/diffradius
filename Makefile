.PHONY: test validate evaluate

test:
	pytest

validate:
	python scripts/validate_benchmark.py

evaluate:
	diffradius evaluate --mode all --output results/benchmark
