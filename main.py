#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import urllib
import urllib2
from google.appengine.api import urlfetch
from bs4 import BeautifulSoup
#import BeautifulSoup
import logging
from webapp2_extras import routes
import urlparse

def getBaseUri(uri):
    idx = uri.rfind('/')
    pidx = uri.find('://')
    if idx == -1 :
        return uri
    if idx == pidx+2 :
        return uri
    return uri[:idx]


def getTopUri(uri):
    pidx = uri.find('://')
    uri2 = uri[pidx+3:]
    idx = uri2.find('/')
    if idx == -1 :
        return uri
    return '%s%s'%(uri[:pidx+3],uri2[:idx])



def convertHTML(origin):
    soup = BeautifulSoup(origin)
    #soup = BeautifulSoup.BeautifulSoup(origin)
    


    links = soup.findAll(attrs={'href':True})
    for link in links :
        if link['href'].startswith('http') :
            hostname = urlparse.urlparse(link['href']).hostname
            url_info = link['href'].split(hostname)
            new_url = '%s%s.web-relay.appspot.com%s'%(url_info[0],hostname, url_info[1])
            link['href'] = new_url
            
    tags = soup.findAll(attrs={'src':True})
    for tag in tags :
        if tag['src'].startswith('http') :
            hostname = urlparse.urlparse(tag['src']).hostname
            url_info = tag['src'].split(hostname)
            new_url = '%s%s.web-relay.appspot.com%s'%(url_info[0],hostname, url_info[1])
            tag['src'] = new_url
 
    tags = soup.findAll(attrs={'action':True})
    for tag in tags :
        if tag['action'].startswith('http') :
            hostname = urlparse.urlparse(tag['action']).hostname
            url_info = tag['action'].split(hostname)
            new_url = '%s%s.web-relay.appspot.com%s'%(url_info[0],hostname, url_info[1])
            tag['action'] = new_url
 
    return soup.renderContents()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        base_domain = self.request.host_url.replace('.web-relay.appspot.com','')
        path_qs = self.request.path_qs
        if base_domain.endswith('web-relay.appspot.com') :
            url = self.request.get('rq')
            if not url :        
                self.response.write('URL:<form action=/><input type=text name=rq value=http://></form>')
                return
            hostname = urlparse.urlparse(url).hostname
            url_info = url.split(hostname)
            new_url = '%s%s.web-relay.appspot.com%s'%(url_info[0], hostname, url_info[1])
            self.response.write("<script> location.href = '%s' </script>"%new_url)
            return
        
        new_url = '%s%s'%(base_domain, path_qs)

        response = urlfetch.fetch(url=new_url, 
                                  method=urlfetch.GET,
                                  headers=self.request.headers)
        self.response.headers = response.headers
        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return

        self.response.write(convertHTML(response.content))

    def post(self):
        base_domain = self.request.host_url.replace('.web-relay.appspot.com','')
        path_qs = self.request.path_qs
        if base_domain.endswith('relay-request.appspot.com') :
            self.response.write('URL:<form action=/><input type=text name=rq value=http://></form>')
            return

        new_url = '%s%s'%(base_domain, path_qs)

        args = urllib.urlencode(self.request.POST)
        response = urlfetch.fetch(url=new_url, 
                                  payload=args,
                                  method=urlfetch.POST,
                                  headers=self.request.headers)
        self.response.headers = response.headers
        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return
        self.response.write(convertHTML(response.content))


app = webapp2.WSGIApplication([
    ('.*', MainHandler),
], debug=True)
