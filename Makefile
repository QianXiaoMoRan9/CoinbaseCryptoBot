run:
	python3 main.py

init:
	source venv/bin/activate

test:
	python3 -m unittest discover -s ./Tidesurf/__test__ -p "*_test.py"