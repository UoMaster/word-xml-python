PYTHON := poetry run python
EXAMPLES_DIR := examples

.PHONY: api demo extract vl vl_v

api:
	$(PYTHON) $(EXAMPLES_DIR)/api_server.py

demo:
	$(PYTHON) $(EXAMPLES_DIR)/quick_demo.py

extract:
	$(PYTHON) $(EXAMPLES_DIR)/word_to_xml.py $(DOCX)

vl:
	export MODEL=vl; $(PYTHON) $(EXAMPLES_DIR)/vl/vl_map_demo.py

vl_v:
	export MODEL=vl_v; $(PYTHON) $(EXAMPLES_DIR)/vl/vl_map_demo.py
