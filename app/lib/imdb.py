from app.config.cplog import CPLog
import base64
import cherrypy
import urllib
import urllib2
import csv

from hashlib import sha1

import json

log = CPLog(__name__)

class ImdbWl:

    watchlist_remove = False

    def __init__(self):
        self.enabled = self.conf('notification_enabled');

    def conf(self, options):
        return cherrypy.config['config'].get('IMDBWatchlist', options)

    def call(self, method, data = {}):
        log.debug("Call method " + method)

        try:
            log.info('Retrieving CSV from %s' % self.conf('url'))
            tmp_csv, headers = urllib.urlretrieve(self.conf('url'), tmp_csv)
#            'http://www.imdb.com/list/export?list_id=watchlist&author_id=ur0034213'
            csvwl = csv.reader(tmp_csv)
            for row in csvwl:
                if row[0] != 'position':
                    watchlist.append(row[1])

        except(IOError):
            log.info("Failed calling method")
            resp = None
        return resp

    def send(self, method, data = {}):
        resp = self.call(method, data)
        if (resp == None):
            return False
        if ("error" in resp):
            log.info("Trakt error message in response: " + resp["error"])
        if (resp["status"] == "success"):
            log.info("Method call successful")
            return True
        else:
            log.info("Method call unsuccessful: " + resp["status"])
            return False

    def notify(self, name, year, imdb_id):
        if not self.enabled:
            return
        
        method = "movie/library/"
        method += "%API%"
        
        data = {
            'movies': [ {
                'imdb_id': imdb_id,
                'title': name,
                'year': year
                } ]
            }
        
        added = self.send(method, data)
        
        if self.watchlist_remove:
            method = "movie/unwatchlist/"
            method += "%API%"
            data = {
                'movies': [ {
                    'imdb_id': imdb_id,
                    'title': name,
                    'year': year
                    } ]
                }
            self.send(method, data)
        
        return added

    def test(self, apikey, username, password):
        self.username = username
        self.password = password
        self.apikey = apikey
        
        method = "account/test/"
        method += "%API%"
        
        return self.send(method)

    def getWatchlist(self):
        method = "user/watchlist/movies.json/%API%/" + self.username
        return self.call(method)
