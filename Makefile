AUTHOR := thombashi
PACKAGE := tabledata
BUILD_DIR := build
BUILD_WORK_DIR := _work
DOCS_DIR := docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build
DIST_DIR := $(BUILD_WORK_DIR)/$(PACKAGE)/dist


.PHONY: build
build:
	@rm -rf $(BUILD_WORK_DIR)/
	@mkdir -p $(BUILD_WORK_DIR)/
	@cd $(BUILD_WORK_DIR); \
		git clone https://github.com/$(AUTHOR)/$(PACKAGE).git; \
		cd $(PACKAGE); \
		python setup.py build
	@twine check $(DIST_DIR)/*
	ls $(DIST_DIR)

.PHONY: clean
clean:
	@rm -rf $(PACKAGE)-*.*.*/ \
		$(BUILD_DIR) \
		$(BUILD_WORK_DIR) \
		dist/ \
		$(DOCS_BUILD_DIR) \
		.eggs/ \
		.pytest_cache/ \
		.tox/ \
		**/*/__pycache__/ \
		*.egg-info/
	@find . -not -path '*/\.*' -type f | grep -E .+\.py\.[a-z0-9]{32,}\.py$ | xargs -r rm

.PHONY: idocs
idocs:
	@pip install --upgrade .
	@make docs

.PHONY: docs
docs:
	@python setup.py build_sphinx --source-dir=$(DOCS_DIR)/ --build-dir=$(DOCS_BUILD_DIR) --all-files

.PHONY: fmt
fmt:
	@black $(CURDIR)
	@autoflake --in-place --recursive --remove-all-unused-imports --exclude "__init__.py" .
	@isort --apply --recursive

.PHONY: readme
readme:
	@cd $(DOCS_DIR); python make_readme.py

.PHONY: release
release:
	@cd $(BUILD_WORK_DIR)/$(PACKAGE); python setup.py release --sign
	@rm -rf $(BUILD_WORK_DIR)
