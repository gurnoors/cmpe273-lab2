from flask import Flask, request, Response, json
import requests, re
from datetime import datetime

import logging
logging.basicConfig(level=logging.DEBUG)
from spyne import Application, rpc, ServiceBase, \
    Integer, Unicode
from spyne import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication


app = Flask(__name__)

am1201 = datetime.strptime('12:01 AM', '%I:%M %p').time()
am3 = datetime.strptime('03:00 AM', '%I:%M %p').time()
am301 = datetime.strptime('03:01 AM', '%I:%M %p').time()
am6 = datetime.strptime('06:00 AM', '%I:%M %p').time()
am601 = datetime.strptime('06:01 AM', '%I:%M %p').time()
am9 = datetime.strptime('09:00 AM', '%I:%M %p').time()
am901 = datetime.strptime('09:01 AM', '%I:%M %p').time()
pm12 = datetime.strptime('12:00 PM', '%I:%M %p').time()
pm1201 = datetime.strptime('12:01 PM', '%I:%M %p').time()
pm3 = datetime.strptime('03:00 PM', '%I:%M %p').time()
pm301 = datetime.strptime('03:01 PM', '%I:%M %p').time()
pm6 = datetime.strptime('06:00 PM', '%I:%M %p').time()
pm601 = datetime.strptime('06:01 PM', '%I:%M %p').time()
pm9 = datetime.strptime('09:00 PM', '%I:%M %p').time()
pm901 = datetime.strptime('09:01 PM', '%I:%M %p').time()
am12 = datetime.strptime('12:00 AM', '%I:%M %p').time()


class HelloWorldService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def checkcrime(self, lat, lon, radius):
        reqStr = "https://api.spotcrime.com/crimes.json?lat=" + lat + "&lon=" + lon + "&radius=" + radius + "&key=."
        resp = requests.get(reqStr).content

        json_data = json.loads(resp)
        json_data = json_data['crimes']
        print len(json_data)

        output = {
            "total_crime": 0,
            "the_most_dangerous_streets": [],
            "crime_type_count": {
                "Assault": 0,
                "Arrest": 0,
                "Burglary": 0,
                "Robbery": 0,
                "Theft": 0,
                "Other": 0,
                'Vandalism': 0
            },
            "event_time_count": {
                "12:01am-3am": 0,
                "3:01am-6am": 0,
                "6:01am-9am": 0,
                "9:01am-12noon": 0,
                "12:01pm-3pm": 0,
                "3:01pm-6pm": 0,
                "6:01pm-9pm": 0,
                "9:01pm-12midnight": 0
            }
        }

        topStreets = {}

        # print am1201
        print "12am is " + str(am12) + " or "
        print "12pm is " + str(pm12) + " or "
        for crime in json_data:
            output['total_crime'] += 1

            # crime_type count
            crime_type = crime['type']
            if crime_type not in output['crime_type_count']:
                output['crime_type_count'][crime_type] = 0
            output['crime_type_count'][crime_type] += 1

            # crime time
            crimeTime = crime['date'][9:]
            time = datetime.strptime(crimeTime, '%I:%M %p').time()
            if time >= am1201 and time <= am3:
                output['event_time_count']["12:01am-3am"] += 1
            elif time >= am301 and time <= am6:
                output['event_time_count']["3:01am-6am"] += 1
            elif time >= am601 and time <= am9:
                output['event_time_count']["6:01am-9am"] += 1
            elif time >= am901 and time <= pm12:
                output['event_time_count']["9:01am-12noon"] += 1
            elif time >= pm1201 and time <= pm3:
                output['event_time_count']["12:01pm-3pm"] += 1
            elif time >= pm301 and time <= pm6:
                output['event_time_count']["3:01pm-6pm"] += 1
            elif time >= pm601 and time <= pm9:
                output['event_time_count']["6:01pm-9pm"] += 1
            elif time > pm901 or time == am12:
                output['event_time_count']['9:01pm-12midnight'] += 1

            # TODO: street
            streets = crime['address'].split("&")
            for street in streets:
                street = re.sub('\d* +block ?o?f?', "", street, flags=re.IGNORECASE)
                # street = re.sub('block of', "", street, flags=re.IGNORECASE)
                # street = re.sub('block', "", street, flags=re.IGNORECASE)
                street = street.strip()
                if street in topStreets:
                    topStreets[street] += 1
                else:
                    topStreets[street] = 1

                """
                for dict in topStreets:
                    if dict is not None:
                        for key in dict:
                            dict[key] += 1
                    else:
                        insDict = {street: 1}
                        topStreets.append(insDict)
                """
        topStreetsList = sorted(topStreets, key=topStreets.get, reverse=True)

        for listEl in topStreets:
            print "key: " + listEl + ", val: " + str(topStreets[listEl])

        print "********************"

        for x in topStreetsList:
            print x

        output['the_most_dangerous_streets'].extend(topStreetsList[:3])

        return output

        # toRet = {'latitude': lat}
        # return Response(json.dumps(toRet))


#@app.route('/checkcrime', methods=['GET'])
#def checkcrime():
#    lat = request.args.get('lat')
#    lon = request.args.get('lon')
#    radius = request.args.get('radius')


#if __name__ == '__main__':
#    app.run(debug='True')

application = Application([HelloWorldService],
    tns='cmpe273.lab2',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()