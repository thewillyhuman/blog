
.PHONY: all build clean

all: clean build

build:
	@echo "Building blog..."
	@cd .engine && python build.py
	@echo "Blog built successfully in the 'public' directory."

clean:
	@echo "Cleaning generated files..."
	@rm -rf public
	@find . -maxdepth 1 -type f -name "*.html" -delete
	@echo "Cleaned generated files."
