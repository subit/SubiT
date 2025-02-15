import sys
sys.path.append("..\\..")
import os

from api.providers.addic7ed import provider as addic7edprovider
Addic7edProvider = addic7edprovider.Addic7edProvider
from api.requestsmanager import get_manager_instance
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest

class TestAddic7edProvider(unittest.TestCase):
    def setUp(self):
        self.provider = Addic7edProvider(
            [Languages.ENGLISH], get_manager_instance("test_addic7ed_provider"))

    def test_get_titles_versions_no_match(self):
        """
        Checks that we get more than single result when the query returns more
        than one title in the site.
        """
        title = MovieTitle("Star Wars")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        # We expect to see 129 Series titles, and 1 Movie title.
        serieses = filter(
            lambda t: isinstance(t, SeriesTitle), titles_versions.titles)
        movies = filter(
            lambda t: isinstance(t, MovieTitle), titles_versions.titles)

        self.assertGreater(len(serieses), 140)
        self.assertGreater(len(movies), 0)

    def test_get_titles_versions_no_title(self):
        """
        Checks that we get an empty list when querying for some random letters.
        """
        title = MovieTitle("silhjkl;sdgsdg sdgfsg")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        self.assertEquals(len(titles_versions), 0)


    def test_get_titles_versions_series_exact(self):
        """
        Simple test to verify that we get version for series. We expect to see
        single SeriesTitle in the result.
        """
        title = SeriesTitle(
            "The Big Bang Theory", 7, 12, "tt3337728",
            "The Hesitation Ramification", 2014, "tt0898266")

        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        # Only single title is expected
        self.assertEqual(len(titles_versions), 1)
        # Only single language
        self.assertEqual(len(titles_versions[0][1]), 1)
        # Four versions (At rank group 1)
        versions = titles_versions[0][1][Languages.ENGLISH][1]
        self.assertEqual(len(versions), 6)

        versions_strings = map(lambda ver: ver[1].version_string, versions)
        # Remove duplications.
        versions_strings = list(set(versions_strings))
        self.assertEquals(
            sorted(versions_strings), 
            ['BDRip.x264.DEMAND', 'DIMENSION', 'WEB-DL'])

        movies_codes = \
            map(lambda ver: ver[1].attributes['movie_code'], versions)
        movies_codes = list(set(movies_codes))
        self.assertEquals(len(movies_codes), 1)
        self.assertEquals(
            movies_codes[0],
            "/serie/The_Big_Bang_Theory/7/12/The_Hesitation_Ramification")
            
        versions_codes = \
            map(lambda ver: ver[1].attributes['version_code'], versions)
        versions_codes = list(set(versions_codes))

        self.assertEquals(
            sorted(versions_codes), 
            [
                "/original/82674/0",
                "/original/82674/1",
                "/original/82674/16",
                "/original/82674/3",
                "/original/82674/4",
                "/updated/1/82674/0"
            ])

    def test_get_titles_versions_movie_exact(self):
        """
        Simple test to verify that we get versions for movie. The query
        returns a single movie in the site.
        """
        title = MovieTitle("Godzilla", 2014, "tt0831387")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        # Only single title is expected
        self.assertEqual(len(titles_versions), 1)
        # Only single language
        self.assertEqual(len(titles_versions[0][1]), 1)
        # Two versions (At rank group 1)
        versions = titles_versions[0][1][Languages.ENGLISH][1]
        self.assertEqual(len(versions), 2)

        self.assertEquals(versions[0][1].version_string, "BluRay_BRrip_BDrip")
        self.assertEquals(versions[1][1].version_string, "WEBRiP-VAiN")

        self.assertEquals(
            versions[0][1].attributes["movie_code"], "/movie/89128")
        self.assertEquals(
            versions[1][1].attributes["movie_code"], "/movie/89128")

        self.assertEquals(
            versions[0][1].attributes["version_code"], "/original/89128/4")
        self.assertEquals(
            versions[1][1].attributes["version_code"], "/original/89128/2")

    def test_get_subtitle_buffer(self):
        """
        Test that given some ProviderVersion, we manage to get the buffer of
        the subtitle.
        """
        title = SeriesTitle("The Big Bang Theory", 7, 12)
        version = ProviderVersion(
            [],
            title,
            Languages.ENGLISH,
            self.provider,
            attributes = {
                "version_code" : "/original/82674/0",
                "movie_code" : "serie/The_Big_Bang_Theory/7/12/The_Hesitation_Ramification"})
        file_name, subtitle_buffer = \
            self.provider.download_subtitle_buffer(version)
        self.assertEquals(
            file_name,
            "The Big Bang Theory - 07x12 - The Hesitation Ramification.DIMENSION.English.HI.C.orig.Addic7ed.com.srt")
        self.assertGreater(len(subtitle_buffer), 31000)



def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        addic7edprovider,
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestAddic7edProvider))
    test_runner.run(tests)