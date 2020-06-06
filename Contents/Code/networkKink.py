import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    shootID = None
    for parts in searchData.title.split():
        if unicode(parts, 'UTF-8').isdigit():
            shootID = parts
            break

    if shootID:
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/shoot/' + shootID
        req = PAutils.HTTPRequest(sceneURL, headers={'Cookie': 'viewing-preferences=straight%2Cgay'})
        detailsPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = detailsPageElements.xpath('//h1[@class="shoot-title"]')[0].text_content().strip()[:-1]
        releaseDate = parse(detailsPageElements.xpath('//span[@class="shoot-date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
        curID = PAutils.Encode(sceneURL)

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[%s] %s [%s] %s' % (shootID, titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=100, lang=lang))
    else:
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//div[@class="shoot-card scene"]'):
            titleNoFormatting = searchResult.xpath('.//img/@alt')[0].strip()
            curID = PAutils.Encode(searchResult.xpath('.//a[@class="shoot-link"]/@href')[0])
            releaseDate = parse(searchResult.xpath('.//div[@class="date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
            shootID = searchResult.xpath('.//span[contains(@class, "favorite-button")]/@data-id')[0]

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[%s] %s [%s] %s' % (shootID, titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="shoot-title"]')[0].text_content().strip()[:-1]

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="description"]')[1].text_content().strip().replace('\n', ' ').replace('Description:', '')

    # Tagline and Collection(s)
    metadata.collections.clear()
    shoot_logo_div = detailsPageElements.xpath('//div[contains(@class, "shoot-logo")]')[0]
    channel = shoot_logo_div.text_content().strip()
    if not channel:
        channel = shoot_logo_div.xpath(".//a/@href")[0].strip()

    if '30minutesoftorment' in channel:
        tagline = '30 Minutes of Torment'
    elif 'animatedkink' in channel:
        tagline = 'Animated Kink'
    elif 'amator' in channel:
        tagline = 'Amator'
    elif 'azianiiron' in channel:
        tagline = 'Aziani Iron'
    elif 'ballgaggers' in channel:
        tagline = 'Ballgaggers'
    elif 'bananajacks' in channel:
        tagline = 'Banana Jacks'
    elif 'bizarrets' in channel:
        tagline = 'Bizarre Video Transsexual'
    elif 'bizarrevideo' in channel:
        tagline = 'Bizarre Video'
    elif 'boundgangbangs' in channel:
        tagline = 'Bound Gangbangs'
    elif 'boundgods' in channel:
        tagline = 'Bound Gods'
    elif 'boundinpublic' in channel:
        tagline = 'Bound in Public'
    elif 'bonusholeboys' in channel:
        tagline = 'Bonus Hole Boys'
    elif 'boundmenwanked' in channel:
        tagline = 'Bound Men Wanked'
    elif 'bondageliberation' in channel:
        tagline = 'Bondage Liberation'
    elif 'brutalsessions' in channel:
        tagline = 'Brutal Sessions'
    elif 'buttmachineboys' in channel:
        tagline = 'Butt Machine Boys'
    elif 'bleufilms' in channel:
        tagline = 'BLEU Films'
    elif 'cfnmeu' in channel:
        tagline = 'CFNM EU'
    elif 'chantasbitches' in channel:
        tagline = 'Chantas Bitches'
    elif 'captivemale' in channel:
        tagline = 'Captive Male'
    elif 'carmenrivera' in channel:
        tagline = 'Carmen Rivera'
    elif 'devicebondage' in channel:
        tagline = 'Device Bondage'
    elif 'devianthardcore' in channel:
        tagline = 'Deviant Hardcore'
    elif 'divinebitches' in channel:
        tagline = 'Divine Bitches'
    elif 'digitalsin' in channel:
        tagline = 'Digital Sin'
    elif 'ddfnetwork' in channel:
        tagline = 'DDF Network'
    elif 'electrosluts' in channel:
        tagline = 'Electrosluts'
    elif 'everythingbutt' in channel:
        tagline = 'Everything Butt'
    elif 'evolvedfightslesbianedition' in channel:
        tagline = 'Evolved Fights Lesbian Edition'
    elif 'evolvedfights' in channel:
        tagline = 'Evolved Fights'
    elif 'familiestied' in channel:
        tagline = 'Families Tied'
    elif 'femdum' in channel:
        tagline = 'FemDum'
    elif 'fetishnetworkmale' in channel:
        tagline = 'Fetish Network Male'
    elif 'fetishnetwork' in channel:
        tagline = 'Fetish Network'
    elif 'fembotacademy' in channel:
        tagline = 'Fembot Academy'
    elif 'footworship' in channel:
        tagline = 'Foot Worship'
    elif 'fuckedandbound' in channel:
        tagline = 'Fucked and Bound'
    elif 'fuckingmachines' in channel:
        tagline = 'Fucking Machines'
    elif 'filthyfemdom' in channel:
        tagline = 'Filthy Femdom'
    elif 'filthsyndicate' in channel:
        tagline = 'Filthy Syndicate'
    elif 'femmefatalefilms' in channel:
        tagline = 'Femme Fatale Films'
    elif 'gloryholesecrets' in channel:
        tagline = 'Glory Hole Secrets'
    elif 'harmonyfetish' in channel:
        tagline = 'Harmony Fetish'
    elif 'hardcoregangbang' in channel:
        tagline = 'Hardcore Gangbang'
    elif 'hardcorepunishments' in channel:
        tagline = 'Hardcore Punishments'
    elif 'hotlegsandfeet' in channel:
        tagline = 'Hot Legs and Feet'
    elif 'hogtiedup' in channel:
        tagline = 'Hogtied Up'
    elif 'hogtied' in channel:
        tagline = 'Hogtied'
    elif 'houseoftaboo' in channel:
        tagline = 'House of Taboo'
    elif 'kinkybites' in channel:
        tagline = 'Kinky Bites'
    elif 'kinkrawtestshoots' in channel:
        tagline = 'Kink Raw Test Shoots'
    elif 'kinktestshoots' in channel:
        tagline = 'Kink Test Shoots'
    elif 'kinkcompilations' in channel:
        tagline = 'Kink Compilations'
    elif 'kinkclassics' in channel:
        tagline = 'Kink Classics'
    elif 'kinkfeatures' in channel:
        tagline = 'Kink Features'
    elif 'kinklive' in channel:
        tagline = 'Kink Live'
    elif 'kinkuniversity' in channel:
        tagline = 'Kink University'
    elif 'lakeviewentertainment' in channel:
        tagline = 'Lakeview Entertainment'
    elif 'machinedom' in channel:
        tagline = 'Machine Dom'
    elif 'menonedge' in channel:
        tagline = 'Men on Edge'
    elif 'meninpain' in channel:
        tagline = 'Men in Pain'
    elif 'meanbitch' in channel:
        tagline = 'Meanbitch'
    elif 'medicalysado' in channel:
        tagline = 'Medicaly Sado'
    elif 'mondofetiche' in channel:
        tagline = 'Mondo Fetiche'
    elif 'nakedkombat' in channel:
        tagline = 'Naked Kombat'
    elif 'pascalssubsluts' in channel:
        tagline = 'Pascals Subsluts'
    elif 'peghim' in channel:
        tagline = 'Peg Him'
    elif 'pegging' in channel:
        tagline = 'Pegging'
    elif 'povpickups' in channel:
        tagline = 'POV Pickups'
    elif 'pornstarplatinum' in channel:
        tagline = 'Pornstar Platinum'
    elif 'publicdisgrace' in channel:
        tagline = 'Public Disgrace'
    elif 'plumperd' in channel:
        tagline = 'Plumperd'
    elif 'revengeofthebaroness' in channel:
        tagline = 'Revenge of the Baroness'
    elif 'royalfetishfilms' in channel:
        tagline = 'Royal Fetish Films'
    elif 'sadisticrope' in channel:
        tagline = 'Sadistic Rope'
    elif 'sisterwives' in channel:
        tagline = 'Sister Wives'
    elif 'severesexfilms' in channel:
        tagline = 'Severe Sex Films'
    elif 'sexualdisgrace' in channel:
        tagline = 'Sexual Disgrace'
    elif 'sexandsubmission' in channel:
        tagline = 'Sex and Submission'
    elif 'sscifidreamgirls' in channel:
        tagline = 'Scifi Dreamgirls'
    elif 'sexandsubmission' in channel:
        tagline = 'Sex and Submission'
    elif 'submissivex' in channel:
        tagline = 'SubmissiveX'
    elif 'submissived' in channel:
        tagline = 'Submissived'
    elif 'straponsquad' in channel:
        tagline = 'Strapon Squad'
    elif 'strugglingbabes' in channel:
        tagline = 'Struggling Babes'
    elif 'sweetfemdom' in channel:
        tagline = 'Sweet Femdom'
    elif 'spizoo' in channel:
        tagline = 'Spizoo'
    elif 'tspussyhunters' in channel:
        tagline = 'TS Pussy Hunters'
    elif 'tsseduction' in channel:
        tagline = 'TS Seduction'
    elif 'twistedvisual' in channel:
        tagline = 'Twisted Visual'
    elif 'thetrainingofo' in channel:
        tagline = 'The Training of O'
    elif 'theupperfloor' in channel:
        tagline = 'The Upper Floor'
    elif 'transerotica' in channel:
        tagline = 'Trans Erotica'
    elif 'tormenttime' in channel:
        tagline = 'Torture Time'
    elif 'venusgirls' in channel:
        tagline = 'Venus Girls'
    elif 'ultimatesurrender' in channel:
        tagline = 'Ultimate Surrender'
    elif 'wasteland' in channel:
        tagline = 'Wasteland'
    elif 'waterbondage' in channel:
        tagline = 'Water Bondage'
    elif 'whippedass' in channel:
        tagline = 'Whipped Ass'
    elif 'wiredpussy' in channel:
        tagline = 'Wired Pussy'
    else:
        Log("Unknown channel: '%s'" % channel)
        tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Studio
    if tagline == 'Chantas Bitches' or tagline == 'Fucked and Bound' or tagline == 'Captive Male':
        metadata.studio = 'Twisted Factory'
    elif tagline == 'Sexual Disgrace' or tagline == 'Strapon Squad' or tagline == 'Fetish Network Male' or tagline == 'Fetish Network':
        metadata.studio = 'Fetish Network'
    else:
        metadata.studio = 'Kink'

    # Release Date
    date = detailsPageElements.xpath('//span[@class="shoot-date"]')[0].text_content().strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//p[@class="tag-list category-tag-list"]//a')
    for genreLink in genres:
        genreName = genreLink.text_content().replace(',', '').strip().title()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//p[@class="starring"]//a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get('href')
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = actorPage.xpath('//div[contains(@class, "biography-container")]//img/@src')[0]

            movieActors.addActor(actorName, actorPhotoURL)

    # Director
    director = metadata.directors.new()
    try:
        directors = detailsPageElements.xpath('//p[@class="director"]/a')
        for dirname in directors:
            director.name = dirname.text_content().strip()
    except:
        pass

    # Posters
    art = []
    xpaths = [
        '//video/@poster',
        '//div[@class="player"]//img/@src',
        '//div[@id="gallerySlider"]//img/@data-image-file'
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            art.append(poster)

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
                if width > 100 and idx > 1:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
