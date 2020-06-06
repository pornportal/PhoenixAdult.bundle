import base64
import codecs
import json
import mimetypes
import os
import re
import os, string, hashlib, base64, re, plistlib, unicodedata, traceback
import random
import re
import requests
import shutil
import time
import urllib
import urlparse
from cStringIO import StringIO
from datetime import datetime
from dateutil.parser import parse
from PIL import Image
import PAactors
import PAgenres
import PAsearchSites
import PAsiteList
import PAutils
import PAsearchData

def has_any(s):
    for v in s:
        if v:
            return True
    return False

def Start():
    HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1MINUTE * 20
    HTTP.Headers['User-Agent'] = PAutils.getUserAgent()
    HTTP.Headers['Accept-Encoding'] = 'gzip'

    requests.packages.urllib3.disable_warnings()

    dateNowObj = datetime.now()
    debug_dir = os.path.realpath('debug_data')
    if os.path.exists(debug_dir):
        for directoryName in os.listdir(debug_dir):
            debugDateObj = parse(directoryName)
            if abs((dateNowObj - debugDateObj).days) > 3:
                debugLogs = os.path.join(debug_dir, directoryName)
                shutil.rmtree(debugLogs)
                Log('Deleted debug data: %s' % directoryName)


def ValidatePrefs():
    Log('ValidatePrefs function call')


class PhoenixAdultAgent(Agent.Movies):
    name = 'PhoenixAdult'
    languages = [Locale.Language.English, Locale.Language.German, Locale.Language.French, Locale.Language.Spanish, Locale.Language.Italian]
    accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.lambda']
    primary_provider = True

    def search(self, results, media, lang):
        Log('*******SEARCH media.name (preferred) ****** ' + str(media.name))
        Log('*******SEARCH media.title****** ' + str(media.title))

        def removeDuplicates(results):
            seen_ids = set()
            for r in results:
                if r.id in seen_ids:
                    results.Remove(r)
                seen_ids.add(r.id)

        try:
            if Prefs['strip_enable']:
                media_name = media.name.split(Prefs['strip_symbol'], 1)[0]
            else:
                media_name = media.name
            self.my_search(results, media, lang, media_name)
        except:
            Log("Error in my_search, trying with media.name, error was: " + traceback.format_exc())

        if has_any(x.score == 100 for x in results):
            Log("Found perfect match, stopping search")
            return

        Log("No perfect match found yet, trying title as well")
        try:
            title = media.title
            if media.primary_metadata is not None:
                title = media.primary_metadata.studio + " " + media.primary_metadata.title
                Log('*******SEARCH using primary_metadata.title****** ' + str(title))

            self.my_search(results, media, lang, title)
        except:
            Log("Error in my_search, trying with filename, error was: " + traceback.format_exc())

        if has_any(x.score == 100 for x in results):
            removeDuplicates(results)
            return

        part = media.items[0].parts[0]
        filename = os.path.basename(part.file)
        self.my_search(results, media, lang, filename)

        removeDuplicates(results)



    def my_search(self, results, media, lang, title):

        Log('*******MEDIA TITLE (unclean) ****** ' + str(title))

        title = getSearchTitle(title)

        Log('***MEDIA TITLE [from media.name]*** %s' % title)
        searchSettings = PAsearchSites.getSearchSettings(title)

        filepath = None
        filename = None
        if media.filename:
            filepath = str(os.path.abspath(urllib.unquote(media.filename)))
            if filepath is None or not (os.path.exists(filepath)):
                part = media.items[0].parts[0]
                filepath = str(os.path.abspath(part.file))
            filename = str(os.path.splitext(os.path.basename(filepath))[0])

        if searchSettings['siteNum'] is None and filepath:
            dirname=os.path.dirname(filepath)
            dirNames=dirname.replace("\\", "/").split('/')
            for directory in reversed(dirNames[1:]):
                newTitle = getSearchTitle(directory)
                Log('***MEDIA TITLE [from directory]*** %s' % newTitle)
                searchSettings = PAsearchSites.getSearchSettings(newTitle)
                if searchSettings['siteNum'] is not None and (searchSettings['searchTitle'] is None or searchSettings['searchTitle'].lower() == PAsearchSites.getSearchSiteName(searchSettings['siteNum']).lower()):
                    combinedTitle = '%s %s' % (newTitle, title)
                    Log('***MEDIA TITLE [from directory + media.name]*** %s' % combinedTitle)
                    searchSettings = PAsearchSites.getSearchSettings(combinedTitle)
                    break

        siteNum = searchSettings['siteNum']

        if siteNum is not None:
            search = PAsearchData.SearchData(media, searchSettings['searchTitle'], searchSettings['searchDate'], filepath, filename)

            provider = PAsiteList.getProviderFromSiteNum(siteNum)
            if provider is not None:
                providerName = getattr(provider, '__name__')
                Log('Provider: %s' % providerName)
                provider.search(results, lang, siteNum, search)

                if Prefs['metadataapi_enable']:
                    if providerName != 'networkMetadataAPI' and (not results or 100 != max([result.score for result in results])):
                        siteNum = PAsearchSites.getSiteNumByFilter('MetadataAPI')
                        if siteNum is not None:
                            provider = PAsiteList.getProviderFromSiteNum(siteNum)
                            if provider is not None:
                                providerName = getattr(provider, '__name__')
                                Log('Provider: %s' % providerName)
                                try:
                                    provider.search(results, lang, siteNum, search)
                                except Exception as e:
                                    Log(e)

        results.Sort('score', descending=True)



    def update(self, metadata, media, lang):
        movieGenres = PAgenres.PhoenixGenres()
        movieActors = PAactors.PhoenixActors()

        HTTP.ClearCache()
        metadata.genres.clear()
        metadata.roles.clear()

        Log('****** CALLED update *******')

        metadata_id = str(metadata.id).split('|')
        siteNum = int(metadata_id[1])
        Log('SiteNum: %d' % siteNum)

        provider = PAsiteList.getProviderFromSiteNum(siteNum)
        if provider is not None:
            providerName = getattr(provider, '__name__')
            Log('Provider: %s' % providerName)
            provider.update(metadata, lang, siteNum, movieGenres, movieActors)

        # Cleanup Genres and Add
        Log('Genres')
        movieGenres.processGenres(metadata)
        metadata.genres = sorted(metadata.genres)

        # Cleanup Actors and Add
        Log('Actors')
        movieActors.processActors(metadata)

        # Add Content Rating
        metadata.content_rating = 'XXX'


def getSearchTitle(title):
    trashTitle = (
        'RARBG', 'COM', r'\d{3,4}x\d{3,4}', 'HEVC', 'H265', 'AVC', r'\dK',
        r'\d{3,4}p', 'TOWN.AG_', 'XXX', 'MP4', 'KLEENEX', 'SD', 'HD',
        'KTR', 'IEVA', 'WRB', 'NBQ', 'ForeverAloneDude',
    )

    for trash in trashTitle:
        title = re.sub(r'\b%s\b' % trash, '', title, flags=re.IGNORECASE)

    title = ' '.join(title.split())

    title = title.replace('"','').replace(":","").replace("!","").replace("[","").replace("]","").replace("(","").replace(")","").replace("&","").replace('RARBG.COM','').replace('RARBG','').replace('180 180x180','').replace('180x180','').replace('Hevc','').replace('H265','').replace('Avc','').replace('5k','').replace(' 4k','').replace('.4k','').replace('2300p60','').replace('2160p60','').replace('1920p60','').replace('1600p60','').replace('2300p','').replace('2160p','').replace('1900p','').replace('1600p','').replace('1080p','').replace('720p','').replace('480p','').replace('540p','').replace('3840x1920','').replace('5400x2700','').replace(' XXX',' ').replace('Ktr ','').replace('MP4-KTR','').replace('Oro ','').replace('Sexors','').replace('3dh','').replace('Oculus','').replace('Oculus5k','').replace('Lr','').replace('-180_','').replace('TOWN.AG_','').strip()

    return title
