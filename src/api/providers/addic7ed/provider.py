import re
import logging
logger = logging.getLogger("subit.api.providers.addic7ed.provider")

from api.providers.iprovider import IProvider
from api.providers.providersnames import ProvidersNames
from api.titlesversions import TitlesVersions
from api.languages import Languages
from api.utils import get_regex_results
from api.title import SeriesTitle
from api.title import MovieTitle


__all__ = ['Addic7edProvider']


class ADDIC7ED_PAGES:
    DOMAIN = 'www.addic7ed.com'
    SEARCH = 'http://%s/search.php?search=%%s' % DOMAIN
    EPISODE_PAGE = 'http://%s/serie/%%s/%%s/%%s/%%s' % DOMAIN

class ADDIC7ED_REGEX:
    # Catches the results of the search result from the main page. For each
    # result, it returns: (TitleUrl, TitleName)
    SEARCH_RESULTS_PARSER = re.compile(
        '(?<=<td><a href=\")(?P<TitleUrl>.*?)(?:\" debug'
        '=\"\d+\">)(?P<TitleName>.*?)(?=</a>)'
    )
    # Catches the results when we query for something, and we're redirected to
    # a specific Title result (specific series episode, etc.). It seems that
    # this behavior (the redirection) only occur for episode, and not for movie
    # titles. The pattern returns: (TitleName, TitleUrl)
    REDIRECT_PAGE_PARSER = re.compile(
        '(?<=\<span class\=\"titulo\"\>)'
        '(?P<TitleName>.*?)(?: \<small\>Subtitle\<\/small\>.*?)'
        # Catches http://www.addic7ed.com
        '(?<=http\:\/\/www\.addic7ed\.com)'
        # Catches /serie/The_Big_Bang_Theory/3/4/The_Pirate_Solution
        '(?P<TitleUrl>\/serie\/[^\/]*\/\d*\/\d*\/[^\/]*?)'
        '(?=\" layout\=\"standard\")'
    )


    class TITLE_PAGE:
        """
        Pattern used for extracting parameters from a title page. An example for
        a title page:
        http://www.addic7ed.com/serie/The_Big_Bang_Theory/7/12/The_Hesitation_Ramification
        """

        # Extracts version string (Named VersionString) of some version, and
        # with it, the associated HTML content that is required in order to
        # extract the rest of the parameters for that version (Named
        # VersionContent).
        RESULT_PAGE_VERSION_SCOPE = re.compile(
            '(?<=Version )(?P<VersionString>.*?)'
            '(?P<VersionContent>, .*?javascript\:saveFavorite.*?)\<\/table\>'
        )
        # When fed with the VersionContent from the previous pattern, extracts
        # the LanguageCode and the HTML content associated with it
        # (LanguageContent).
        VERSION_SCOPE_LANGUAGE_SCOPE = re.compile(
            'saveFavorite\(\d+,(?P<LanguageCode>\d+),\d+\).*?'
            '(?P<LanguageContent>\<a class\=\"buttonDownload\" .*?'
            '\<\/a\>\<\/td\>)'
        )
        # When fed with the LanguageContent, extract the URL for the subtitle
        # under DownloadUrl.
        LANGUAGE_SCOPE_DOWNLOAD_URL = re.compile(
            '\<a class\=\"buttonDownload\" href\=\"(?P<DownloadUrl>.*?)\"\>'
        )
        # Splits the string that is defined as the version string in the page.
        # i.e., from "720p Web-DL" to ['720p', 'Web', 'DL'].
        VERSION_STRING_SPLITTER = re.compile('[\.,-_ ]')

class Addic7edProvider(IProvider):
    """ The provider implementation for www.Addic7ed.com. """

    provider_name = ProvidersNames.ADDIC7ED
    # A mapping between the Language object and Addic7ed's own language code.
    addic7ed_code_to_language = {
        '23' : Languages.HEBREW,
        '1'  : Languages.ENGLISH,
        '4'  : Languages.SPANISH,
        '38' : Languages.ARABIC,
        '35' : Languages.BULGARIAN,
        '25' : Languages.SLOVAK,
        '16' : Languages.TURKISH,
        '14' : Languages.CZECH,
        '19' : Languages.RUSSIAN,
        '29' : Languages.NORWEGIAN,
        '18' : Languages.SWEDISH,
        '8'  : Languages.FRENCH,
        '2'  : Languages.GREEK
    }
    supported_languages = addic7ed_code_to_language.values()

    def __init__(self, languages, requests_manager):
        super(Addic7edProvider, self).__init__(languages, requests_manager)

    def _get_provider_versions(self, title, page_content):
        provider_versions = []
        for version, language, url in \
            extract_versions_parameters_from_title_page(page_content):

            lang_obj = Addic7edProvider.addic7ed_code_to_language[language]
            idetifiers = ADDIC7ED_REGEX.TITLE_PAGE\
                .VERSION_STRING_SPLITTER.split(version)

            provider_version = ProviderVersion(
                identifiers, title, lang_obj, self, version, {'url' : url})
            logger.debug("Constructed ProviderVersion: %s" % provider_version)
            provider_versions.append(provider_version)
        return provider_versions

    def _get_titles_versions(self, page_content):
        titles_versions = TitlesVersions()
        for title_url, title_name in \
            extract_title_parameters_from_search_page(page_content):




    def get_title_versions(self, title, version):
        """
        If the title is series, will try to access the episode's page directly,
        and if succeeded, will return the version in that page. If the series 
        is missing numbering, and contains only the episode name, it will use 
        it in the query.

        If the title is movie, 
        """
        logger.debug("Received call to get_title_version with %s,%s" %
            title, version)

        

        # It's a series, lets try accessing the page directly.
        if isinstance(title, SeriesTitle) and title.got_numbering:
            url = get_episode_url()
            logger.debug("Trying to access the episode's page directly: " url)
            title_page_content = self.requests_manager.perform_request_text(url)
            provider_versions = \
                self._get_provider_versions(title, title_page_content)
            logger.debug("Got %d versions." % len(provider_versions))
            # Only stop and return if we got results, otherwise, we'll proceed
            # to the regular query.
            if provider_versions:
                return TitlesVersions(provider_versions)

        query = get_query_string(title)
        query_url = format_query_url(query)
        query_page_content = \
            self.requests_manager.perform_request_text(query_url)



        search_results = get_regex_results(
            ADDIC7ED_REGEX.SEARCH_RESULTS_PARSER, search_content, True)

        titles_versions = TitlesVersions()

        # It means no redirection occurred.
        if search_results:
            logger.debug(
                "The regex for the search page matched. "
                "No redirection occurred.")
        # We need to parse the versions.
        else:
            pass

    def download_subtitle_buffer(self, provider_version):
        pass

def get_query_string(title):
    """
    Returns the query string for Addic7ed's. For movies it returns simply the
    name value, for series, it will return the name and the season_number and
    episode_number concatenated with 'x' between them (i.e, for episode 3 in
    season 10, it produces 10x3). If the episode name is specified and the
    episode numbering is missing, the name will be used instead.

    >>> from api.title import MovieTitle, SeriesTitle
    >>> print get_query_string(MovieTitle("The Matrix"))
    The Matrix
    >>> print get_query_string(SeriesTitle("The Big Bang Theory", 7, 12))
    The Big Bang Theory 7x12
    >>> print get_query_string(SeriesTitle("The Big Bang Theory", 7, 12, \
        "The Hesitation Ramification"))
    The Big Bang Theory 7x12
    >>> print get_query_string(SeriesTitle("The Big Bang Theory", \
        episode_name = "The Hesitation Ramification"))
    The Big Bang Theory The Hesitation Ramification
    """
    query = title.name
    if isinstance(title, SeriesTitle):
        query += " "
        if title.season_number:
            query += "%dx%d" % (title.season_number, title.episode_number)
        else:
            query += title.episode_name
    return query

def format_query_url(query):
    """
    Generates a well-formatted url string in order for it to be used as the
    search URL in Addic7ed.

    >>> print format_query_url("The Matrix")
    http://www.addic7ed.com/search.php?search=The%20Matrix
    >>> print format_query_url("Some Title With (Brackets)")
    http://www.addic7ed.com/search.php?search=Some%20Title%20With%20%28Brackets%29
    """
    from urllib2 import quote as url_quote
    return ADDIC7ED_PAGES.SEARCH % url_quote(query)

def get_episode_url(title):
    """
    Constructs the url for the episode given in the title instance. If the title
    is missing the episode name, `zzz` will be used instead. If either the 
    episode or the season number is missing, exception will be raised.

    >>> from api.title import SeriesTitle
    >>> t = SeriesTitle("The 4400", 2, 5, episode_name="As Fate Would Have It")
    >>> print get_episode_url(t)
    http://www.addic7ed.com/serie/the%204400/2/5/as%20fate%20would%20have%20it
    >>> t = SeriesTitle("The 4400", 2, 5)
    >>> print get_episode_url(t)
    http://www.addic7ed.com/serie/the%204400/2/5/zzz
    >>> t = SeriesTitle("The 4400", episode_name="As Fate Would Have It")
    >>> print get_episode_url(t)
    Traceback (most recent call last):
        ...
    InvalidTitleValue: The episode title must contain numbering.
    """
    logger.debug("Constructing URL for title: %s" % title)
    if not title.got_numbering:
        from api.exceptions import InvalidTitleValue
        raise InvalidTitleValue("The episode title must contain numbering.")

    from urllib2 import quote as url_quote
    return ADDIC7ED_PAGES.EPISODE_PAGE % (
        url_quote(title.name.lower()), 
        title.season_number, 
        title.episode_number,
        url_quote(title.episode_name.lower()) or "zzz")

def extract_title_parameters_from_search_page(page_content):
    """ 
    Extracts parameters from the search result. Each item in the list is in the 
    format of: (title_url, title_name). 

    >>> import requests
    >>> content = requests.get(\
        r"http://www.addic7ed.com/search.php?search=Godzilla").content
    >>> stripped_content = content.replace("\\r", "")
    >>> stripped_content = stripped_content.replace("\\t", "")
    >>> stripped_content = stripped_content.replace("\\n", "")
    >>> print extract_title_parameters_from_search_page(stripped_content)
    [('movie/89128', 'Godzilla (2014)')]

    >>> content = requests.get(\
        r"http://www.addic7ed.com/search.php?search=lost+s04e12").content
    >>> stripped_content = content.replace("\\r", "")
    >>> stripped_content = stripped_content.replace("\\t", "")
    >>> stripped_content = stripped_content.replace("\\n", "")
    >>> titles = extract_title_parameters_from_search_page(stripped_content)
    >>> titles = sorted(titles)
    >>> print titles[0]
    ('serie/Lost/4/12/There%C2%B4s_no_place_like_home_%28I%29', 'Lost - 04x12 - There\\xc2\\xb4s no place like home (I)')
    >>> print titles[1]
    ('serie/Lost_Girl/4/12/It_Begins', 'Lost Girl - 04x12 - It Begins')
    """
    return get_regex_results(ADDIC7ED_REGEX.SEARCH_RESULTS_PARSER, page_content)

def extract_versions_parameters_from_title_page(page_content):
    """
    Given page content that is associated with some title page in the site,
    extracts all the attributes of the version from it (using the re patterns
    specified above). Assumes that any white spaces was removed (except for
    single spaces). Each item in the list is a tuple in the format of:
    (VersionString, LanguageCode, DownloadUrl)

    >>> import requests
    >>> r = requests.get(\
        r"http://www.addic7ed.com/serie/The_Big_Bang_Theory/7/12/The_Hesitation_Ramification")
    >>> content = r.content
    >>> stripped_content = content.replace("\\r", "")
    >>> stripped_content = stripped_content.replace("\\t", "")
    >>> stripped_content = stripped_content.replace("\\n", "")
    >>> versions = extract_versions_parameters_from_title_page(stripped_content)
    >>> len(versions)
    23
    >>> for v in sorted(versions): print v
    ('720p Web-DL', '10', '/original/82674/11')
    ('BDRip.x264.DEMAND', '1', '/original/82674/16')
    ('DIMENSION', '1', '/original/82674/0')
    ('DIMENSION', '1', '/original/82674/1')
    ('DIMENSION', '1', '/updated/1/82674/0')
    ('DIMENSION', '10', '/updated/10/82674/1')
    ('DIMENSION', '35', '/updated/35/82674/0')
    ('DIMENSION', '8', '/updated/8/82674/1')
    ('Dimension', '17', '/original/82674/5')
    ('Dimension', '17', '/updated/17/82674/5')
    ('LOL', '10', '/original/82674/2')
    ('LOL', '11', '/original/82674/9')
    ('LOL', '17', '/original/82674/10')
    ('LOL', '19', '/original/82674/14')
    ('LOL', '19', '/original/82674/15')
    ('LOL', '7', '/original/82674/7')
    ('ROVERS', '17', '/original/82674/13')
    ('WEB-DL', '1', '/original/82674/3')
    ('WEB-DL', '1', '/original/82674/4')
    ('WEB-DL', '10', '/original/82674/6')
    ('WEB-DL', '17', '/original/82674/8')
    ('WEB-DL', '17', '/updated/17/82674/8')
    ('WEB-DL', '7', '/original/82674/12')
    """
    versions = []

    regex_class = ADDIC7ED_REGEX.TITLE_PAGE

    # For each version.
    for version_string, content in get_regex_results(
        regex_class.RESULT_PAGE_VERSION_SCOPE, page_content):
        # For each language.
        for language_code, content in get_regex_results(
            regex_class.VERSION_SCOPE_LANGUAGE_SCOPE, content):
            # For each download url.
            for download_url in get_regex_results(
                regex_class.LANGUAGE_SCOPE_DOWNLOAD_URL, content):

                versions.append((version_string, language_code, download_url))

    return versions

def construct_title_from search_result(title_url, title_name):
    """
    Given a single result from the search page (parsed), returns either a 
    MovieTitle or SeriesTitle with the appropriate attributes.

    >>> construct_title_from('movie/89128', 'Godzilla (2014)')
    <MovieTitle name='Godzilla', year=2014, imdb_id=''>
    >>> construct_title_from('serie/Lost_Girl/4/12/It_Begins', 'Lost Girl - 04x12 - It Begins')
    <SeriesTitle name='Lost Girl', season_number=4, episode_number=12, episode_name='It Begins' ...>
    """
    pass