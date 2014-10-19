prefix=/usr/local

install:
	install -m 0755 mesecode.py $(prefix)/bin

.PHONY: install