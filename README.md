# BiCaption 


## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/rhythmanand6/photoshop.git
$ cd Photoshop
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ virtualenv2 --no-site-packages env
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies:
```sh
(env)$ cd PhotoHub
(env)$ python manage.py runserver
```
And navigate to `http://localhost:8000/`.


<a href = "https://github.com/rhythmanand/Python/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo = rhythmanand6/photoshop"/>
</a>
