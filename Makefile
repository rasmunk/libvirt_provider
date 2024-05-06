PACKAGE_NAME=libvirt_provider
PACKAGE_NAME_FORMATTED=$(subst -,_,$(PACKAGE_NAME))

.PHONY: all init clean dist distclean maintainer-clean
.PHONY: install uninstall installcheck check

all: venv install-dep init

init:
ifeq ($(shell test -e defaults.env && echo yes), yes)
ifneq ($(shell test -e .env && echo yes), yes)
		ln -s defaults.env .env
endif
endif

clean: distclean venv-clean
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

dist:
	$(VENV)/python setup.py sdist bdist_wheel

distclean:
	rm -fr dist build $(PACKAGE_NAME).egg-info $(PACKAGE_NAME_FORMATTED).egg-info

maintainer-clean: distclean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

install-dev:
	$(VENV)/pip install -r requirements-dev.txt

uninstall-dev:
	$(VENV)/pip uninstall -y -r requirements-dev.txt

install-dep:
	$(VENV)/pip install -r requirements.txt

install: install-dep
	$(VENV)/pip install .

uninstall:
	$(VENV)/pip uninstall -y -r requirements.txt
	$(VENV)/pip uninstall -y $(PACKAGE_NAME)

installcheck:
	$(VENV)/pip install -r tests/requirements.txt

uninstallcheck:
	$(VENV)/pip uninstall -y -r requirements.txt

check_pre:
	. $(VENV)/activate; python3 setup.py check -rms

check_init:
	@echo "Checking if the dummy ssh target is running for the tests"
	if [ -z "$$(docker ps -q -f 'name=ssh_dummy_target')" ]; then \
		@echo "Starting dummy ssh target"; \
		docker run -d --rm --name ssh_dummy_target -p 2222:22 ucphhpc/ssh-mount-dummy:latest; \
		@echo @Waiting for the dummy ssh target to start; \
		@sleep 10; \
	else \
		echo "Dummy ssh target is already running"; \
	fi

# The tests requires access to the docker socket
check: check_pre check_init
	. $(VENV)/activate; pytest -s -v tests/

include Makefile.venv