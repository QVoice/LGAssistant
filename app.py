#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

from pyfcm import FCMNotification

# Flask app should start in global layout
app = Flask(__name__)

def sendFCM():
    url = 'https://fcm.googleapis.com/fcm/send'
    body = {
        "data":{
            "title":"mytitle",
            "body":"mybody"
        },
        "to": "fqfSBcsFu7A:APA91bH8Ob2tgbirkUBAjPSwF4kZJGto5fFMousw8hRWo6AkutpIkFLauecEzSNUDtJoug92RJ7D1bVcq32rX5sWiIIKvNQwgZHswU2xIrYlsAS8BHrBQSvPuJVaV0117tqRwBn0dq1z"
    }

    headers = {"Content-Type":"application/json", "Authorization":"key=AAAAPll10tw:APA91bFgF4IU5k7V4-YBEphx9k7y7z0pqyhGcnN3Qbk8Wjuglftq8MzBa_ST75j4HSNh0YaonJov0BtTtq_85i8ao0Fm92JlDit96xLY5UJiC_OVwfFNvpYJnFU5FRYA7M8O20i2ahEi"}
    r = requests.post(url, data=json.dumps(body), headers=headers)
    print(r)
    return r

def sendNoti():
    push_service = FCMNotification(api_key="AAAAPll10tw:APA91bFgF4IU5k7V4-YBEphx9k7y7z0pqyhGcnN3Qbk8Wjuglftq8MzBa_ST75j4HSNh0YaonJov0BtTtq_85i8ao0Fm92JlDit96xLY5UJiC_OVwfFNvpYJnFU5FRYA7M8O20i2ahEi")
    registration_id="fqfSBcsFu7A:APA91bH8Ob2tgbirkUBAjPSwF4kZJGto5fFMousw8hRWo6AkutpIkFLauecEzSNUDtJoug92RJ7D1bVcq32rX5sWiIIKvNQwgZHswU2xIrYlsAS8BHrBQSvPuJVaV0117tqRwBn0dq1z"
    message = "Hope you're having fun this weekend, don't forget to check today's news"
    result = push_service.notify_single_device(registration_id=registration_id, message_body=message, message_title="title")
    print(result)
    return None

def test():
    URL = 'http://www.tistory.com'
    response = requests.get(URL)
    print('test status: ')
    print(response.status_code)
    return None

@app.route('/webhook', methods=['POST'])
def webhook():
    test()
    
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    #res = processRequest(req)

    speech = "Battery is running out mostly when you are playing games. Plus, turning  off your GPS  when it is not in use may help."
    res = {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "LGAssistant"
    }

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    #if req.get("result").get("action") != "yahooWeatherForecast":
    if req.get("result").get("action") != "smartdoctor.battery":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    result = urllib.request.urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    
    #for test
    city = "Boston"
    
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        #"source": "apiai-weather-webhook-sample"
        "source": "lg-assistant"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    
    app.run(debug=False, port=port, host='0.0.0.0')

