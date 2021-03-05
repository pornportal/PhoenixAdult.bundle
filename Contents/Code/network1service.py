import PAsearchSites
import PAutils
import json
import os, io
import glob


def get_Token(siteNum):
    url = PAsearchSites.getSearchBaseURL(siteNum)
    token_key = urlparse.urlparse(url).hostname

    token = None
    if token_key and token_key in Dict:
        data = Dict[token_key].split('.')[1] + '=='
        data = base64.b64decode(data).decode('UTF-8')
        if json.loads(data)['exp'] > time.time():
            token = Dict[token_key]

    if not token:
        req = PAutils.HTTPRequest(url, 'HEAD')
        if 'instance_token' in req.cookies:
            token = req.cookies['instance_token']

    if token_key and token:
        if token_key not in Dict or Dict[token_key] != token:
            Dict[token_key] = token
            Dict.Save()

    return token


def findMetadata(media, sceneID):
    metadataSearchDirs = PAsearchSites.findMetadataDirs(media)
    metadataSearchFileName = "/**/*-%s-*.json" % (sceneID)
    Log("Trying to find metadata via json files: " + str(metadataSearchDirs) + ", SearchQuery: " + metadataSearchFileName)
    items = []
    if len(metadataSearchDirs) > 0:
        for d in metadataSearchDirs:
            globStr = d + metadataSearchFileName
            Log("Trying glob: " + globStr)
            for m in glob.glob(globStr):
                with io.open(m) as json_file:
                    item = json.load(json_file)
                    items.append(item)
    return items


def search(results, lang, siteNum, searchData):
    token = get_Token(siteNum)
    headers = {
        'Instance': token,
    }

    sceneID = None
    parts = searchData.title.split()
    firstPart = PAsearchSites.safeUnicode(parts[0])
    if firstPart.isdigit():
        sceneID = firstPart
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

    Log('****** Project1 ID ' + str(sceneID) + ' *******')

    def handleSearchResultItem(results, searchResult):
        titleNoFormatting = searchResult['title']
        releaseDate = parse(searchResult['dateReleased']).strftime('%Y-%m-%d')
        curID = searchResult['id']
        siteName = searchResult['brand'].title()
        subSite = ''
        if 'collections' in searchResult and searchResult['collections']:
            subSite = searchResult['collections'][0]['name']
        siteDisplay = '%s/%s' % (siteName, subSite) if subSite else siteName

        if sceneID:
            score = 100 - Util.LevenshteinDistance(sceneID, curID)
        elif searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        if sceneType == 'trailer':
            titleNoFormatting = '[%s] %s' % (sceneType.capitalize(), titleNoFormatting)
            score = score - 10

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, sceneType), name='%s [%s] %s' % (titleNoFormatting, siteDisplay, releaseDate), score=score, lang=lang))

    for sceneType in ['scene', 'movie', 'serie', 'trailer']:
        if sceneID: # and not searchData.title:
            url = PAsearchSites.getSearchSearchURL(siteNum) + '/v2/releases?type=%s&id=%s' % (sceneType, sceneID)
        else:
            url = PAsearchSites.getSearchSearchURL(siteNum) + '/v2/releases?type=%s&search=%s' % (sceneType, searchData.encoded)

        req = PAutils.HTTPRequest(url, headers=headers)
        if req:
            searchResults = req.json()['result']
            for searchResult in searchResults:
                handleSearchResultItem(results, searchResult)

    # Fallback to json file
    if len(results) < 1:
        # Find metadata folder/file
        for item in findMetadata(media, sceneID):
            handleSearchResultItem(results, item['result'])

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneID = metadata_id[0]
    sceneType = metadata_id[2]

    token = get_Token(siteNum)
    headers = {
        'Instance': token,
    }
    url = PAsearchSites.getSearchSearchURL(siteNum) + '/v2/releases?type=%s&id=%s' % (sceneType, sceneID)
    req = PAutils.HTTPRequest(url, headers=headers)
    resultData = req.json()['result']
    if len(resultData) > 0: 
        detailsPageElements = resultData[0]
    else:
        # Fallback to metadata json file
        metadataSearchDirs = PAsearchSites.findMetadataDirs(media)
        detailsPageElements = findMetadata(media, sceneID)[0]['result']

    # Studio
    metadata.studio = detailsPageElements['brand'].title()

    # Title
    metadata.title = detailsPageElements['title']

    # Summary
    description = None
    if 'description' in detailsPageElements:
        description = detailsPageElements['description']
    elif 'parent' in detailsPageElements:
        if 'description' in detailsPageElements['parent']:
            description = detailsPageElements['parent']['description']

    if description:
        metadata.summary = description

    # Studio
    metadata.studio = detailsPageElements['brand'].title()

    # Tagline and Collection(s)
    metadata.collections.clear()
    seriesNames = []

    if 'collections' in detailsPageElements and detailsPageElements['collections']:
        for collection in detailsPageElements['collections']:
            seriesNames.append(collection['name'])
    if 'parent' in detailsPageElements:
        if 'title' in detailsPageElements['parent']:
            seriesNames.append(detailsPageElements['parent']['title'])

    isInCollection = False
    siteName = PAsearchSites.getSearchSiteName(siteNum).lower().replace(' ', '').replace('\'', '')
    for seriesName in seriesNames:
        if seriesName.lower().replace(' ', '').replace('\'', '') == siteName:
            isInCollection = True
            break

    # This allows one to 'hide' the 'main' Site collection while still showing 'unsorted' stuff
    if len(seriesNames) < 1:
        seriesNames.insert(0, PAsearchSites.getSearchSiteName(siteNum) + " (Unsorted)")

    if not isInCollection:
        seriesNames.insert(0, PAsearchSites.getSearchSiteName(siteNum))

    for seriesName in seriesNames:
        metadata.collections.add(seriesName)

    # Release Date
    date_object = parse(detailsPageElements['dateReleased'])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements['tags']
    for genreLink in genres:
        genreName = genreLink['name']

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements['actors']
    for actorLink in actors:
        actorPageURL = PAsearchSites.getSearchSearchURL(siteNum) + '/v1/actors?id=%d' % actorLink['id']

        req = PAutils.HTTPRequest(actorPageURL, headers=headers)
        actorResultData = req.json()['result']
        actorData = actorResultData[0]
        if len(actorResultData) > 0:
            actorData = actorResultData[0]
        else:
            # Try again via 'correct' brand
            actorSiteNum = PAsearchSites.getSiteNumByFilter(detailsPageElements['brand'])
            if actorSiteNum != siteNum:
                Log("Could not find actor data, trying again with with brand '%s'" % (detailsPageElements['brand']))
                token = get_Token(actorSiteNum)
                headers = {
                    'Instance': token,
                }
                
                req = PAutils.HTTPRequest(actorPageURL, headers=headers)
                actorResultData = req.json()['result']
                if len(actorResultData) > 0:
                    actorData = actorResultData[0]
                else:
                    actorData = None
            else:
                actorData = None 

        if actorData:
            actorName = actorData['name']
            actorPhotoURL = ''
            if actorData['images'] and actorData['images']['profile']:
                actorPhotoURL = actorData['images']['profile']['0']['xs']['url']

                movieActors.addActor(actorName, actorPhotoURL)
        else:
            Log("Could not find actor data (image) for ID '%s' and name '%s'" % (actorLink['id'], actorLink['name']))
            actorName = actorLink['name']
            movieActors.addActor(actorName, '')

    # Posters
    art = []
    for imageType in ['poster', 'cover']:
        if imageType in detailsPageElements['images']:
            for image in detailsPageElements['images'][imageType]:
                if image.isdigit():
                    art.append(detailsPageElements['images'][imageType][image]['xx']['url'])

    for imageType in ['poster', 'cover']:
        if 'parent' in detailsPageElements and 'images' in detailsPageElements['parent'] and imageType in detailsPageElements['parent']['images']:
            for image in detailsPageElements['parent']['images'][imageType]:
                art.append(image['xx']['url'])

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
