PYTHON := poetry run python
EXAMPLES_DIR := examples

.PHONY: api demo extract vlmap

api:
	$(PYTHON) $(EXAMPLES_DIR)/api_server.py

demo:
	$(PYTHON) $(EXAMPLES_DIR)/quick_demo.py

extract:
	$(PYTHON) $(EXAMPLES_DIR)/word_to_xml.py $(DOCX)

vlmap:
	$(PYTHON) $(EXAMPLES_DIR)/vl_map_demo.py
