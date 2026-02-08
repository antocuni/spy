# Makefile for building SPy external dependencies.
#
# Usage:
#   make bdwgc TARGET=native
#
# This downloads, builds, and installs bdwgc as a static library.
# The built artifacts are placed in build/<TARGET>/

BDWGC_VERSION := 8.2.8
BDWGC_TARBALL := downloads/gc-$(BDWGC_VERSION).tar.gz
BDWGC_SRC := src/gc-$(BDWGC_VERSION)
BDWGC_URL := https://github.com/ivmai/bdwgc/releases/download/v$(BDWGC_VERSION)/gc-$(BDWGC_VERSION).tar.gz

ifeq ($(TARGET),)
    $(error TARGET is required. Usage: make bdwgc TARGET=native)
endif

PREFIX := $(CURDIR)/build/$(TARGET)

.PHONY: bdwgc clean

bdwgc: $(PREFIX)/lib/libgc.a

# Download
$(BDWGC_TARBALL):
	mkdir -p downloads
	curl -L -o $@ $(BDWGC_URL)

# Extract
$(BDWGC_SRC)/configure: $(BDWGC_TARBALL)
	mkdir -p src
	tar xzf $< -C src
	touch $@

# Configure + build + install
$(PREFIX)/lib/libgc.a: $(BDWGC_SRC)/configure
	mkdir -p $(PREFIX)/_build
	cd $(PREFIX)/_build && \
		$(CURDIR)/$(BDWGC_SRC)/configure \
			--prefix=$(PREFIX) \
			--disable-shared \
			--enable-static \
			--disable-java-finalization \
			--disable-gcj-support \
			CFLAGS="-fPIC -O2"
	$(MAKE) -C $(PREFIX)/_build -j$$(nproc)
	$(MAKE) -C $(PREFIX)/_build install

clean:
	rm -rf build src downloads
