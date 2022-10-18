PREFIX?=/usr
BINPREFIX?=$(PREFIX)/bin
LIBPREFIX?=$(PREFIX)/lib/fulgurate
MANPREFIX?=$(PREFIX)/man
DOCPREFIX?=$(PREFIX)/share/doc/fulgurate
PYTHON?=python2
A2X?=a2x

TEMP=build/tmp
VENV=$(TEMP)/venv
MANSRC=$(TEMP)/man/src
MANOUT=$(TEMP)/man/out
PROGS=$(addprefix fulgurate-, run import show-schedule)
MANPAGES=fulgurate.1 $(addsuffix .1, $(PROGS))
DOCS=example.tsv example-filter.sh example-finish.sh

all: man

$(TEMP):
	mkdir -p $<

$(VENV)/.sentinel:
	rm -rf $(VENV)
	$(PYTHON) -m virtualenv $(VENV)
	source $(VENV)/bin/activate; pip install --upgrade .

$(MANSRC)/fulgurate-%.txt: $(VENV)/.sentinel
	mkdir -p $(MANSRC)
	( \
		source $(VENV)/bin/activate; \
		echo fulgurate-$* | tr 'a-z' 'A-Z' | sed -e 's|$$|(1)|g'; \
		echo fulgurate-$* | sed -e 's|.|=|g;s|$$|===|g'; \
		python -c "from fulgurate.cmd_line import _$(subst -,_,$*) as cmd; print cmd.__doc__"; \
		echo -e "SEE ALSO\n--------\n'fulgurate(1)'"; \
	) > $@

$(MANSRC)/fulgurate.txt: fulgurate-man README
	mkdir -p $(MANSRC)
	./$< > $@

$(MANOUT)/%.1: $(TEMP)/man/src/%.txt
	mkdir -p $(MANOUT)
	$(A2X) -f manpage -L $< -D $(MANOUT)

man: $(addprefix $(MANOUT)/, $(MANPAGES))

install: man
	$(PYTHON) setup.py install --prefix="$(PREFIX)/"
	mkdir -p $(MANPREFIX)/man1
	cp -f $(addprefix $(MANOUT)/, $(MANPAGES)) $(MANPREFIX)/man1
	mkdir -p $(DOCPREFIX)
	cp -f $(DOCS) $(DOCPREFIX)

.PHONY: install

clean:
	find src -name '*.py' -exec rm {} \;
	rm -rf $(TEMP) build
	rm -rf *.pyc $(MANTEMPNAME).py $(MANTEMPNAME).txt $(MANPAGES)
