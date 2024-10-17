Note:   &::  -it's a comment

- install python

given below commands all work in windows command prompt

only on initial deployment,
follow commands in cmd as in project location

>pip install virtualenv &::to install python package for creating virtual environment <br/>
>python -m venv env  &::to create virtual environment <br/>
>env\scripts\activate  &::to activating virtual environment <br/>
>pip install -r requirements.txt  &::to install requirements on virtual environment <br/>
>python manage.py runserver  &::to run server <br/>

to deactivate the environment
>env\scripts\deactivate

if only normal host
>env\scripts\activate  &::only if environment is not activated <br/>
>python manage.py runserver  &::to host project

