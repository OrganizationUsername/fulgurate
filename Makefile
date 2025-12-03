PREFIX?=/usr
BINPREFIX?=$(PREFIX)/bin
LIBPREFIX?=$(PREFIX)/lib/fulgurate
MANPREFIX?=$(PREFIX)/man
DOCPREFIX?=$(PREFIX)/share/doc/fulgurate
PYTHON?=python3
A2X?=a2x

VENV=venv.make
MANOUT=man
MANPROGS=$(addprefix fulgurate-, run import-cards show-schedule)
MANPAGES=$(addsuffix .1, $(MANPROGS))
DOCS=example.tsv example-filter.sh example-finish.sh
PYTHONREQS=setuptools tox argparse-manpage

all: test man

$(VENV)/.sentinel:
	rm -rf $(VENV)
	$(PYTHON) -m virtualenv $(VENV)
	( \
		source $(VENV)/bin/activate; \
		pip install --upgrade pip; \
		pip install --upgrade $(PYTHONREQS); \
		pip install --upgrade .[cmd-line] \
	)

test: $(VENV)/.sentinel
	( \
		source $(VENV)/bin/activate; \
		tox \
	)


$(addprefix $(MANOUT)/, $(MANPAGES)): $(VENV)/.sentinel
	( \
		source $(VENV)/bin/activate; \
		python setup.py build_manpages \
	)

man: $(addprefix $(MANOUT)/, $(MANPAGES))

install: man
	$(PYTHON) setup.py install --prefix="$(PREFIX)/"
	mkdir -p $(MANPREFIX)/man1
	cp -f $(addprefix $(MANOUT)/, $(MANPAGES)) $(MANPREFIX)/man1
	mkdir -p $(DOCPREFIX)
	cp -f $(DOCS) $(DOCPREFIX)

.PHONY: install

clean:
	rm -rf $(VENV) $(MANOUT)
