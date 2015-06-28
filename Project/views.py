from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.http import Http404
import json
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from datetime import date,timedelta,datetime
import urllib
import urllib2
import requests
import random
import string
import os
from geopy.geocoders import Nominatim
from django.conf import settings
SITE_URL = 'home/bitnami/apps/django/django_projects/Project/'

def getResponse(data):
    try:
        response = HttpResponse(json.dumps(data),mimetype='application/json')
    except:
        response = HttpResponse(json.dumps(data),content_type='application/json')
    return response
@csrf_exempt
def api_v1_canvas(request):
    if request.method == 'POST':
        try:
            geolocator = Nominatim()
            location = None
            access_token = request.POST.get('access_token')
            print "access_token:" + access_token
            text_location = request.POST.get('text_location')
            gps_location = request.POST.get('gps_location').decode('utf8') 

            if text_location:
                geo = geolocator.geocode(text_location)
                if hasattr(geo, 'latitude') and hasattr(geo, 'longitude'):
                    print geo.latitude
                    print geo.longitude
                    location = str(geo.latitude) + "," + str(geo.longitude)
                else:
                    pass
            else:
                location = str(gps_location)
                print "location: " + location
                pass
            filename = parse_places_api(location, access_token)
        except Exception,e:
            print e
        return HttpResponse(json.dumps({'success':True,'filename':filename}), content_type="application/javascript; charset=utf-8") 
        
def parse_places_api(location, access_token):
    json_http_response = []
    query = '*'
    url = 'https://graph.facebook.com/search'
    payload= {
        'q':query,
        'center':location,
        'type':'place',
        'access_token':access_token,
        'limit':5
    }
    r = requests.get(url,params=payload)
    json_response = json.loads(r.text)
    print json_response
    data = json_response['data']
    print data
    count = len(json_response['data'])
    max_pagination = 1
    retries = 0
    while ('next' in json_response['paging'] and retries < max_pagination):
        try:
            url = json_response['paging']['next']
            r = requests.get(url)
            json_response = json.loads(r.text) 
            data.extend(json_response['data'])
            retries += 1
        except:
            print "no data in next field"
            continue
    for eachResult in data:
        try:
            count = count -1
            print eachResult['id']
            placeDetails = get_place_details(eachResult['id'], access_token)
            
            json_http_response.append(placeDetails)
            
        except Exception, e:
            #print e
            print "Data could not be saved"
            continue

    try:
        filename = ''.join(random.choice(string.lowercase) for x in range(10))
        dir = os.path.dirname('/'+SITE_URL+'/'+filename+'.json')
        if not os.path.exists(dir):
            os.makedirs(dir)
        fo = open('/'+SITE_URL+'/'+filename+'.json', "w+")
        fo.seek(0, 2)
        line = fo.write( json.dumps(json_http_response) )
    except Exception,e:
        print e
    return filename

def get_place_details(placeId, access_token):
    ''' This method gets details of places using facebook graph api '''
    try:
        data = {}
        url = 'https://graph.facebook.com/' + placeId + '?fields=photos.limit(1).type(profile),location,friends,checkins,name,description,id,category&access_token=' + access_token
        r = requests.get(url)
        json_response = json.loads(r.text)
        friends_checkins = json_response['friends_checkins']
        if friends_checkins < 1:
            return data
        checkins = json_response['checkins']
        longitude = json_response['location']['longitude']
        latitude = json_response['location']['latitude']
        place_id = json_response['id']
        title = json_response['name'].encode('utf-8')
        if 'description' not in json_response:
            description=""
        else:
            description = json_response['description']
        category = json_response['category']
        if 'photos' not in json_response:
            profile_pic = '/'+SITE_URL+'/static/location-512.png'
        else:
            profile_pic = json_response['photos']['data'][0]['source']
        url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q='+ title + " places"
        img = requests.get(url)
        img_json_response = json.loads(img.text)
        images = img_json_response['responseData']['results'][0]['unescapedUrl'] + ","+ img_json_response['responseData']['results'][1]['unescapedUrl'] + ","+img_json_response['responseData']['results'][2]['unescapedUrl'] + ","+img_json_response['responseData']['results'][3]['unescapedUrl']
        data = { 'title' : str(title), 'image' : str(profile_pic), 'rating' : 3.0, 'releaseYear' : 2014, 'genre' : ['action', 'drama'], 'latitude':latitude, 'longitude':longitude, 'checkins':checkins, 'category':category, 'id':place_id, 'description': description,'images':images }
    except Exception,e:
        print e
        pass
    return data