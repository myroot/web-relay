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
    pattern = r'[\'" =]+(http://([^\/\'\" ]+))'
    #pattern = r'(http://([^\/ ]+))'
    p = re.compile(pattern)
    r = p.findall(origin)
    for domain in r :
        if domain[1].find('web-relay.appspot.com') == -1 :
            domainList.add(domain[0])
    
    #pattern = r'(https://([^\/ ]+))'
    pattern = r'[\'" =]+(https://([^\/\'\" ]+))'
    p = re.compile(pattern)
    r = p.findall(origin)
    for domain in r :
        if domain[1].find('web-relay.appspot.com') == -1 :
            domainList.add(domain[0])

    changed = origin
    for item in domainList : 
        changed = changed.replace(item, '%s.web-relay.appspot.com'%(item))

    #change adsense client
    pattern = r'google_ad_client = \"([^\"]+)\"'
    changed = re.sub(pattern, r'google_ad_client = "ca-pub-9683070520101388"', changed)

    pattern = r'google_ad_client = \"([^\"]+)\".*google_ad_slot = \"([^\"]+)\".*google_ad_width = (\d+);.*google_ad_height = (\d+);'
    p = re.compile(pattern, re.S)
    r = p.findall(changed)
    for item in r :
        logging.info(item)
        if item[2] == '728' and item[3] == '90' :
            changed = changed.replace(item[1], '3544012565')
        elif item[2] == '160' and item[3] == '600' :
            changed = changed.replace(item[1], '5020745763')
        elif item[2] == '120' and item[3] == '240' :
            changed = changed.replace(item[1], '6497478963')
        elif item[2] == '300' and item[3] == '250' :
            changed = changed.replace(item[1], '4881144963')
        elif item[2] == '336' and item[3] == '280' :
            changed = changed.replace(item[1], '6357878168')
        elif item[2] == '320' and item[3] == '50' :
            changed = changed.replace(item[1], '7834611366')
        elif item[2] == '120' and item[3] == '600' :
            changed = changed.replace(item[1], '9311344561')
        elif item[2] == '300' and item[3] == '600' :
            changed = changed.replace(item[1], '1788077760')
        elif item[2] == '200' and item[3] == '200' :
            changed = changed.replace(item[1], '3264810961')



    return changed


class MainHandler(webapp2.RequestHandler):
    def get(self):
        #logging.info(dir(self.request))
        logging.info('host_url : '+ self.request.host_url)
        logging.info('path : '+ self.request.path)
        logging.info('path_qs : '+ self.request.path_qs)
        logging.info('url : '+ self.request.url)
        logging.info('uri : '+ self.request.uri)
        logging.info('host : '+ self.request.host)


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
            logging.info('%s:%s'%(header,headers[header]))
            if header == 'Host' or header == 'Referer':
                headers[header] = headers[header].replace('.web-relay.appspot.com','')


        response = urlfetch.fetch(url=new_url, 
                                  method=urlfetch.GET,
                                  headers=headers,
                                  follow_redirects=False, 
                                  deadline=10)

        #logging.info("------------------------------------")
        logging.info('status = %d'%response.status_code)
        resHeaders = response.headers

        if resHeaders.has_key('content-length') :
            resHeaders.pop('content-length')

        if resHeaders.has_key('location') :
            if resHeaders['location'].startswith('http') :
                location_host = urlparse.urlparse(resHeaders['location']).hostname
                url_info = resHeaders['location'].split(location_host)
                new_location = '%s%s.web-relay.appspot.com%s'%(url_info[0], location_host, url_info[1])
                resHeaders['location'] = new_location
                pass
            elif resHeaders['location'].startswith('/') :
                resHeaders['location'] = '%s.web-relay.appspot.com%s'%(base_domain,resHeaders['location'])
            else:
                base_path = self.request.path
                if base_path == '/':
                    base_path = ''
                resHeaders['location'] = '%s.web-relay.appspot.com%s/%s'%(base_domain,base_path,resHeaders['location'])
        if resHeaders.has_key('set-cookie') :
            pattern = r'domain=([^;,]+)'
            resHeaders['set-cookie'] = re.sub(pattern,r'domain=\1.web-relay.appspot.com',resHeaders['set-cookie'])

        self.response.headers = resHeaders
        self.response.status_int = response.status_code

        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return

        #logging.info('contents:%s'%response.content)
        self.response.write(replaceDomain(response.content))

    def post(self):
        logging.info('host_url : '+ self.request.host_url)
        logging.info('path : '+ self.request.path)
        logging.info('path_qs : '+ self.request.path_qs)
        logging.info('url : '+ self.request.url)
        logging.info('uri : '+ self.request.uri)
        logging.info('host : '+ self.request.host)

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

        try:
            args = urllib.urlencode(self.request.POST)
        except:
            arglist = []
            for i in self.request.POST.keys():
                t = '%s=%s'%(i,self.request.POST[i])
                arglist.append(t)
            args = '&'.join(arglist)

        response = urlfetch.fetch(url=new_url, 
                                  payload=args,
                                  method=urlfetch.POST,
                                  headers=headers,
                                  follow_redirects=False,
                                  deadline=10)

        resHeaders = response.headers
        for header in resHeaders.keys() :
            logging.info('%s:%s'%(header,resHeaders[header]))
        logging.info('contents:%s'%response.content)

        if resHeaders.has_key('content-length') :
            resHeaders.pop('content-length')

        if resHeaders.has_key('location') :
            if resHeaders['location'].startswith('http') :
                logging.info('location :%s'%resHeaders['location'])
                location_host = urlparse.urlparse(resHeaders['location']).hostname
                url_info = resHeaders['location'].split(location_host)
                if len(url_info) == 1 :
                    url_info = [url_info[0],'']
                new_location = '%s%s.web-relay.appspot.com%s'%(url_info[0], location_host, url_info[1])
                resHeaders['location'] = new_location
                pass
            elif resHeaders['location'].startswith('/') :
                resHeaders['location'] = '%s.web-relay.appspot.com%s'%(base_domain,resHeaders['location'])
            else:
                base_path = self.request.path
                if base_path == '/':
                    base_path = ''
                resHeaders['location'] = '%s.web-relay.appspot.com%s/%s'%(base_domain,base_path,resHeaders['location'])
        
        if resHeaders.has_key('set-cookie') :
            pattern = r'domain=([^;,]+)'
            resHeaders['set-cookie'] = re.sub(pattern,r'domain=\1.web-relay.appspot.com',resHeaders['set-cookie'])
            logging.info('converted cookie:%s',resHeaders['set-cookie'])
        
        self.response.headers = resHeaders
        self.response.status_int = response.status_code

        if response.headers.has_key('Content-Type') and not response.headers['Content-Type'].startswith("text") :
            self.response.write(response.content)
            return
        self.response.write(replaceDomain(response.content))

app = webapp2.WSGIApplication([
    ('.*', MainHandler),
], debug=True)
