from zipfile import ZipFile
from cStringIO import StringIO
from redis import Redis
from models import IP, City
import requests
import json


GEO_BASE_FILE = 'http://ipgeobase.ru/files/db/Main/geo_files.zip'
CHARSET = 'windows-1251'
COUNTRY_CODES = ['RU']


def file_list_content(zip_file, name):

    try:
        content = zip_file.read(name)
        content = content.decode(CHARSET).strip().split('\n')
        content = filter(None, content)
    except KeyError:
        print 'File {name} not exists in archive!'.format(name=name)
        exit()

    return content


def update():

    r = Redis()

    cities_keys = r.keys('City:*')
    if cities_keys:
        r.delete(*cities_keys)

    ip_keys = r.keys('IP:*')
    if ip_keys:
        r.delete(*ip_keys)

    print 'Start download geo base file.'
    base_file = requests.get(GEO_BASE_FILE)

    if base_file.status_code != requests.codes.ok:
        print 'File not available!'
        return base_file.status_code

    file_buffer = StringIO(base_file.content)
    zip_file = ZipFile(file_buffer)

    print 'Processing.'

    cities = file_list_content(zip_file, 'cities.txt')
    cidr_optim = file_list_content(zip_file, 'cidr_optim.txt')

    for x in cities:

        x = filter(None, x.split('\t'))
        city_id = int(x[0])

        if len(x) >= 5 and city_id:

            coordinates = map(float, eval(str(x[-2:])))

            obj_city = City()
            obj_city.id = city_id
            obj_city.city = x[1]
            obj_city.region = x[2]
            obj_city.territory = x[3]
            obj_city.coordinates = coordinates
            obj_city.save()

    for x in cidr_optim:

        x = filter(None, x.split('\t'))

        if len(x) >= 5:

            ip_start = int(x[0])
            ip_end = int(x[1])

            ip_city_id = x[4]

            if ip_city_id and ip_city_id != '-' and ip_start and ip_end:

                ip_city_id = int(ip_city_id)

                city_obj = City.objects.get_by_id(ip_city_id)

                if city_obj:

                    if x[3] not in COUNTRY_CODES:
                        city_obj.delete()
                        continue

                    if not city_obj.country:
                        city_obj.country = x[3]
                        city_obj.save()

                    obj_ip = IP()
                    obj_ip.start_range = ip_start
                    obj_ip.end_range = ip_end
                    obj_ip.city = city_obj
                    obj_ip.save()

                    r.incr('IP:count')

    cities_dump = {x.city: x.slug for x in City.objects.all()}
    r.set('City:slug', json.dumps(cities_dump))

    zip_file.close()
    file_buffer.close()

    print 'End.'


update()
