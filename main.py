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
import logging
import urlparse
import re

def replaceDomain(origin):
    domainList = set()
    pattern = r'[\'" ]+(http://([^\/\'\" ]+))'
    #pattern = r'(http://([^\/ ]+))'
    p = re.compile(pattern)
    r = p.findall(origin)
    for domain in r :
        if domain[1].find('web-relay.appspot.com') == -1 :
            domainList.add(domain[0])
    
    #pattern = r'(https://([^\/ ]+))'
    pattern = r'[\'" ]+(https://([^\/\'\" ]+))'
    p = re.compile(pattern)
    r = p.findall(origin)
    for domain in r :
        if domain[1].find('web-relay.appspot.com') == -1 :
            domainList.add(domain[0])

    changed = origin
    for item in domainList : 
        changed = changed.replace(item, '%s.web-relay.appspot.com'%(item))
    return changed



class MainHandler(webapp2.RequestHandler):
    def get(self):
        base_domain = self.request.host_url.replace('.web-relay.appspot.com','')
        path_qs = self.request.path_qs
        if base_domain.endswith('web-relay.appspot.com') :
            url = self.request.get('rq')
            if not url :        
                self.response.write('URL:<form action=/><input type=text name=rq value=http://></form>')
                return
            url = path_qs.split('rq=')[-1]
            url = url.replace('%3A',':').replace('%2F','/')
            hostname = urlparse.urlparse(url).hostname
            url_info = url.split(hostname)
            new_url = '%s%s.web-relay.appspot.com%s'%(url_info[0], hostname, url_info[1])
            self.response.write("<script> location.href = '%s' </script>"%new_url)
            return
        
        new_url = '%s%s'%(base_domain, path_qs)

        headers = self.request.headers
        for header in headers.keys():
            if header == 'Host' or header == 'Referer':
                headers[header] = headers[header].replace('.web-relay.appspot.com','')

        response = urlfetch.fetch(url=new_url, 
                                  method=urlfetch.GET,
                                  headers=headers)

        self.response.headers = response.headers
        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return

        self.response.write(replaceDomain(response.content))

    def post(self):
        base_domain = self.request.host_url.replace('.web-relay.appspot.com','')
        path_qs = self.request.path_qs
        if base_domain.endswith('relay-request.appspot.com') :
            self.response.write('URL:<form action=/><input type=text name=rq value=http://></form>')
            return

        new_url = '%s%s'%(base_domain, path_qs)

        headers = self.request.headers
        for header in headers.keys():
            if header == 'Host' or header == 'Referer':
                headers[header] = headers[header].replace('.web-relay.appspot.com','')


        args = urllib.urlencode(self.request.POST)
        response = urlfetch.fetch(url=new_url, 
                                  payload=args,
                                  method=urlfetch.POST,
                                  headers=headers)

        self.response.headers = response.headers
        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return
        self.response.write(replaceDomain(response.content))

app = webapp2.WSGIApplication([
    ('.*', MainHandler),
], debug=True)
