PROJECT_NAME := system_builder

MK_DIR := makefiles

export PROJECT_NAME

.PHONY: clean GEN_HTML HTML_CLEAN GEN_PDF PDF_CLEAN

all: GEN_HTML GEN_PDF

GEN_HTML:
	$(MAKE) -f $(MK_DIR)/makehtml.mk

GEN_PDF: GEN_HTML
	$(MAKE) -f $(MK_DIR)/makepdf.mk

clean: HTML_CLEAN PDF_CLEAN

HTML_CLEAN:
	$(MAKE) -f $(MK_DIR)/makehtml.mk clean

PDF_CLEAN:
	$(MAKE) -f $(MK_DIR)/makepdf.mk clean

