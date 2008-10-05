.PHONY: clean server test

server:
	python manage.py runserver 8001

clean: 
	rm -f *.pyc *.pyo
	rm -f admin/*.pyc admin/*.pyo
