check: mypy pyupgrade black


pyupgrade:
	pyupgrade --exit-zero-even-if-changed --py36-plus arkimaps $(shell find arkimapslib -name "*.py")

black:
	black arkimaps arkimapslib/

mypy:
	mypy arkimaps arkimapslib tests
