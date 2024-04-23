PYTHON_ENVIRONMENT := PYTHONASYNCDEBUG=1 PYTHONDEBUG=1

check: mypy pyupgrade black

pyupgrade:
	pyupgrade --exit-zero-even-if-changed --py36-plus arkimaps $(shell find arkimapslib -name "*.py")

black:
	black arkimaps arkimapslib/

mypy:
	mypy arkimaps arkimapslib tests

unittest:
	$(PYTHON_ENVIRONMENT) python3 -m unittest discover tests

coverage:
	$(PYTHON_ENVIRONMENT) python3 -m coverage erase
	$(PYTHON_ENVIRONMENT) python3 -m coverage run -p -m unittest discover tests
	$(PYTHON_ENVIRONMENT) python3 -m coverage combine
	$(PYTHON_ENVIRONMENT) python3 -m coverage html
	$(PYTHON_ENVIRONMENT) python3 -m coverage report -m

.PHONY: check pyupgrade black mypy unittest coverage
