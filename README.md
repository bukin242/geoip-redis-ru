# geoip-redis-ru
This service uses ipgeobase.ru database from Russian IP block.
For storage data uses Redis server.
For http gateway uses wsgi protocol.
Output JSON format.
Support JSONP method, set and get callback function on execute to JavaScript.
Fast speed if uses receiver and this service on the local host.


### Required software must be install for example "How to start"
```
sudo apt-get install python-pip python-virtualenv virtualenvwrapper redis-server
```

### How to start

* Runserver
```
$ mkvirtualenv wsgi
$ pip install -r requirements.txt
$ python update.py
$ python wsgi.py
```
 
  
See http://127.0.0.1:8000/ output result.

* Periodically update the database
```
$ python update.py
```

### Example output
```
{"city": "Челябинск", "coordinates": [55.159889, 61.40258], "country": "RU", "ip": "88.206.122.101", "region": "Челябинская область", "slug": "cheliabinsk", "territory": "Уральский федеральный округ"}
```

Get JSONP
```
http://127.0.0.1:8000/?callback=MyFunction
```

Get all city slug list
```
http://127.0.0.1:8000/slug/
```
