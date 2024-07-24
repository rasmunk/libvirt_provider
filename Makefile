PACKAGE_NAME=libvirt_provider
PACKAGE_NAME_FORMATTED=$(subst -,_,$(PACKAGE_NAME))

.PHONY: all init clean dist distclean maintainer-clean
.PHONY: install uninstall installtest test

all: venv install-dep init

init:
ifeq ($(shell test -e defaults.env && echo yes), yes)
ifneq ($(shell test -e .env && echo yes), yes)
		ln -s defaults.env .env
endif
endif

clean: distclean venv-clean
	rm -fr .env
	rm -fr *.lock
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

dist: venv
	$(VENV)/python setup.py sdist bdist_wheel

distclean:
	rm -fr dist build $(PACKAGE_NAME).egg-info $(PACKAGE_NAME_FORMATTED).egg-info

maintainer-clean: distclean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

install-dev: venv
	$(VENV)/pip install -r requirements-dev.txt

uninstall-dev: venv
	$(VENV)/pip uninstall -y -r requirements-dev.txt

install-dep: venv
	$(VENV)/pip install -r requirements.txt

install: install-dep
	$(VENV)/pip install .

uninstall: venv
	$(VENV)/pip uninstall -y -r requirements.txt
	$(VENV)/pip uninstall -y $(PACKAGE_NAME)

installtest: install
	$(VENV)/pip install -r tests/requirements.txt

uninstalltest: venv
	$(VENV)/pip uninstall -y -r requirements.txt

test_pre: venv 
	. $(VENV)/activate; python3 setup.py check -rms
	. $(VENV)/activate; rstcheck README.rst

test_smoke: venv
	. $(VENV)/activate; pytest -m smoke -s -v tests/

test: test_pre
	. $(VENV)/activate; pytest -m 'not smoke' -s -v tests/

include Makefile.venv