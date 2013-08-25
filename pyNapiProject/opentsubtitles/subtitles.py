# -*- coding: utf-8 -*- 
from xmlrpclib import ServerProxy
import os
import base64

class StatusError(Exception): pass
class NoSubtitlesError(Exception): pass
class FileNotExistError(OSError): pass
class GetSubtitlesError(Exception): pass

class StatusParsser:
    def __init__(self, data):
        self.data = data
    def parse(self):
        return self.data['status']


class ParseIncomingData:
    def __init__(self, data):
        self.data = data
    
    def _is_status_ok(self, status):
        if status == SubtitlesConncector.RETURNED_OK_STATUS:
            return True
        return False
    
    def _check_status(self):
        self.status = StatusParsser(self.data).parse()
        if self._is_status_ok(self.status):
            return True
        return False
    
    def _is_find_subtitles(self):
        self.finded_subtitles = self.data['data']
        if not self.finded_subtitles:
            return False
        return True
    
    def parse(self):
        if self._check_status():        
            if self._is_find_subtitles():
                return self.finded_subtitles
            else:
                raise NoSubtitlesError, "Subtitles not found" 
        else:
            raise StatusError, status
        
class ParseSubtitlesToSend:
    def __init__(self, data):
        self.data = data
        
    def parse(self):
        output = {}
        for pro in self.data.__dict__:
            if self.data.__dict__[pro]:
                output[pro] = self.data.__dict__[pro]
        return output

class FileProperties:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def get_file_size(self):
        try:
            size = str(os.path.getsize(self.file_path))
            return size
        except OSError:
            raise FileNotExistError, "No souch file {0}".format(self.file_path)
    
    def get_file_hash(self):
        from hash import hashFile
        try:
            hash = str(hashFile(self.file_path))
            return hash
        except IOError:
            raise FileNotExistError, "No souch file {0}".format(self.file_path)
        
class SubtitlesConncector:
    RETURNED_OK_STATUS = '200 OK'
    
    def __init__(self, user_name = '', password = '', language = '', agent = 'OS Test User Agent'):
        self.user_name = user_name
        self.password = password
        self.language = language
        self.agent = agent
        self._api_adres = 'http://api.opensubtitles.org/xml-rpc'
        self.proxy_server = ServerProxy(self._api_adres)
        self.token = self._get_token()
            
    def _is_status_ok(self, status):
        if status == SubtitlesConncector.RETURNED_OK_STATUS:
            return True
        return False
        
    def _get_token(self):
        data = self.proxy_server.LogIn(self.user_name, self.password, self.language, self.agent)
        status = StatusParsser(data = data).parse()
        if self._is_status_ok(status):
            return data['token']
        else:
            raise StatusError, status
    
    def _save_zip(self, data_to_zip, path, file_name):
        b64img = base64.b64decode(data_to_zip)
        b64imgfile = open(str(path + "/" + file_name + ".zip"), 'w')			
        b64imgfile.write(b64img)

    def get_subtitles(self, subtitle, subtitles_dir = None):
        if not subtitles_dir:
            subtitles_dir = os.path.expanduser("~") + "/subtitles"	 
        if not os.path.exists(subtitles_dir):
            os.makedirs(subtitles_dir)
        data = self.proxy_server.DownloadSubtitles(self.token, [subtitle.idsubtitlefile])
        try:
            data = data['data'][0]['data']
        except Exception:
            raise GetSubtitlesError, "Error: cant get data"     
        self._save_zip(data, subtitles_dir, subtitle.subfilename)
    
    def search_subtitles(self, subtitles):
        parsed_data_to_send = ParseSubtitlesToSend(subtitles).parse()
        data = self.proxy_server.SearchSubtitles(self.token, [parsed_data_to_send])
        data = ParseIncomingData(data).parse()
        collect = SubtitlesFindedCollection()
        for d in data:
            collect.append(SubtitlesFindedProperties(sublangid = d['SubLanguageID'], subfilename = d['SubFileName'], idsubtitlefile = d['IDSubtitleFile']))
        return collect

class SubtitlesFindedCollection(list):
    def __init__(self, **args):
        list.__init__(self, **args)

    def search_by_id(self, id):
        for subtitles in self:
            if subtitles.idsubtitlefile == id:
                return subtitles

class SubtitlesFindedProperties:
    def __init__(self, sublangid, subfilename, idsubtitlefile):
        self.sublangid = sublangid
        self.subfilename = subfilename
        self.idsubtitlefile = idsubtitlefile
        
class SubtitlesSearchProperties:
    
    def __init__(self, sublanguageid = '', moviehash = '', moviebytesize = '',
                 imdbid = '', query = '', season = '', episode = '', tag = ''):
        self.sublanguageid = sublanguageid
        self.moviehash = moviehash
        self.moviebytesize = moviebytesize
        self.imdbid = imdbid
        self.query = query
        self.season = season
        self.episode = episode
        self.tag = tag
        
    def __str__(self):
        return "<{0}>".format(self.moviehash)
        
