.PHONY: install run

# Install target to set up the virtual environment and install dependencies
install:
	python -m venv venv
	pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

# Run target to activate the virtual environment and start the FastAPI server
run:
	. venv/bin/activate && uvicorn main:app --reload
