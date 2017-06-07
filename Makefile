all: install

BINDIR = /usr/local/bin
CURDIR = $(shell pwd)

install:
	cd toolbox/supsictrl; python setup.py install
	cd toolbox/supsisim; python setup.py install
	cd CodeGen; rm -rf lib; mkdir lib
	cd CodeGen/devices; make; make install
	cd $(BINDIR); rm -f pyEdit pyRTPLT* pyParams gen_pydev loadnrt
	cp BlockEditor/gen_pydev $(BINDIR)/
	ln -s $(CURDIR)/BlockEditor/pyEdit.py $(BINDIR)/pyEdit
	ln -s $(CURDIR)/BlockEditor/pyRTPlt.py $(BINDIR)/pyRTPlt
	ln -s $(CURDIR)/BlockEditor/pyRTPltXY.py $(BINDIR)/pyRTPltXY
	ln -s $(CURDIR)/BlockEditor/pyParams.py $(BINDIR)/pyParams
	cp DriverNRT/loadnrt $(BINDIR)


