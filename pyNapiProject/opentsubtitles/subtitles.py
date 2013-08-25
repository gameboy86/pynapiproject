# -*- coding: utf-8 -*- 
from xmlrpclib import ServerProxy
import os
import base64

class StatusError(Exception): pass
class NoSubtitlesError(Exception): pass
class FileNotExistError(OSError): pass

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
    
    def get_subtitles(self, subtitle):
        home_path = os.path.expanduser("~")
        full_path = home_path+"/subtitles"
        if not os.path.exists(full_path):
            print "tworze folder {0}".format(full_path)
            os.makedirs(full_path)
        array_to_send = []
        array_to_send.append(subtitle.idsubtitlefile)
        data = self.proxy_server.DownloadSubtitles(self.token, array_to_send)
        data = data['data'][0]['data']
        b64img = base64.b64decode(data)
        all = full_path+"/" + subtitle.subfilename + ".zip"
        b64imgfile = open(str(all), 'w')
        b64imgfile.write(b64img)
        print data
    
    def search_subtitles(self, subtitles):
        parsed_data_to_send = ParseSubtitlesToSend(subtitles).parse()
        array_to_send =[]
        array_to_send.append(parsed_data_to_send)
        data = self.proxy_server.SearchSubtitles(self.token, array_to_send)
        data = ParseIncomingData(data).parse()
        c = SubtitlesFindedCollection()
        for a in data:
            c.append(SubtitlesFindedProperties(sublangid = a['SubLanguageID'], subfilename = a['SubFileName'], idsubtitlefile = a['IDSubtitleFile']))
        return c

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
        
        
if __name__ == "__main__":
    try:
        test = SubtitlesConncector(user_name = '', password = '')
    except StatusError as e:
        print e
    
    f = FileProperties("/home/gameboy/Pobrane/pygame-1.9.1release/The.Hobbit.An.Unexpected.Journey.2012.720p.BluRay.x264-SPARKS/The.Hobbit.An.Unexpected.Journey.2012.720p.BluRay.x264-SPARKS.mkv").get_file_hash()
    z = FileProperties("/home/gameboy/Pobrane/pygame-1.9.1release/The.Hobbit.An.Unexpected.Journey.2012.720p.BluRay.x264-SPARKS/The.Hobbit.An.Unexpected.Journey.2012.720p.BluRay.x264-SPARKS.mkv").get_file_size()

    subtitles = SubtitlesSearchProperties(moviebytesize = z, moviehash = f)
    data = test.search_subtitles(subtitles)
    print data
    for a in data['data']:
        print a
        