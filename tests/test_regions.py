"""Unit tests for India location verification and hub tagging in scraper.regions."""
import unittest
from scraper.regions import get_city_tag, is_india_job


class TestRegions(unittest.TestCase):
    def test_is_india_job(self):
        cases = [
            (["Bengaluru, Karnataka, India"], True),
            (["Hyderabad, Telangana"], True),
            (["Pune, India"], True),
            (["Gurgaon, Haryana, India"], True),
            (["Noida, UP"], True),
            (["Chennai, Tamil Nadu"], True),
            (["Mumbai, Maharashtra"], True),
            (["Remote (India)"], True),
            (["Remote - India"], True),
            (["India"], True),
            # Negative test cases: must not match false positives
            (["Indianapolis, IN, United States"], False),
            (["Indiana, USA"], False),
            (["Jakarta, Indonesia"], False),
            (["London, United Kingdom"], False),
            (["San Francisco, CA"], False),
            (["Singapore"], False),
            ([], False),
            ([""], False),
        ]
        for locs, expected in cases:
            with self.subTest(locations=locs):
                self.assertEqual(is_india_job(locs), expected)

    def test_get_city_tag(self):
        cases = [
            (["Bengaluru, India"], "Bengaluru"),
            (["Bangalore, Karnataka"], "Bengaluru"),
            (["BLR"], "Bengaluru"),
            (["Hyderabad, India"], "Hyderabad"),
            (["Secunderabad"], "Hyderabad"),
            (["Cyberabad"], "Hyderabad"),
            (["Pune, Maharashtra"], "Pune"),
            (["Gurugram, Haryana"], "Delhi-NCR"),
            (["Noida, India"], "Delhi-NCR"),
            (["Delhi, India"], "Delhi-NCR"),
            (["Chennai, Tamil Nadu"], "Chennai"),
            (["Mumbai, India"], "Mumbai"),
            (["Navi Mumbai"], "Mumbai"),
            (["Remote, India"], "Remote (India)"),
            (["India Remote"], "Remote (India)"),
            (["Kolkata, West Bengal"], "India (Multiple/Other)"),
        ]
        for locs, expected in cases:
            with self.subTest(locations=locs):
                self.assertEqual(get_city_tag(locs), expected)


if __name__ == "__main__":
    unittest.main()
