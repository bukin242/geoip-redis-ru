from json import dumps, loads
from webob import Request
from models import IP
from redis import Redis
from iptools.ipv4 import ip2long, validate_ip, LOCALHOST


CHARSET = 'utf-8'


def application(env, start_response):

    r = Redis()
    request = Request(env)
    ip = request.params.get('ip')

    if ip:
        if validate_ip(ip) and ip != LOCALHOST:
            ip = ip.encode(request.url_encoding)
        else:
            ip = None
    else:
        ip = request.remote_addr

    callback = request.params.get('callback')
    headers = []

    if callback:
        callback = callback.encode(request.url_encoding)
        headers.append(('Content-Type', 'application/javascript; charset=' + CHARSET))
    else:
        headers.append(('Content-Type', 'application/json; charset=' + CHARSET))
        headers.append(('Access-Control-Allow-Origin', '*'))

    status = '200 OK'
    start_response(status, headers)

    dump = {}

    if request.path == '/slug/':
        dump = loads(r.get('City:slug'))

    else:
        count = r.get('IP:count')

        if ip and count:
            long_ip = ip2long(ip)
            get_object = IP.objects.zfilter(end_range__gte=long_ip)
            obj = None

            for x in xrange(3):
                get_object = get_object.limit(1, x)

                if get_object and long_ip > get_object[0].start_range:
                    obj = get_object[0]
                    break

            if obj is not None:

                dump.update({'ip': ip})
                dump.update(obj.city.attributes_dict)

    response_body = dumps(dump, sort_keys=True).decode('unicode-escape').encode(CHARSET)

    if callback:
        return [callback, '(', response_body, ')']
    else:
        return [response_body]


if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(application, host='0.0.0.0', port='8000')
