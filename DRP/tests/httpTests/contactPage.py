#!/usr/bin/env python
"""This package provides tests for the Contact page."""

from .httpTest import GetHttpTest, PostHttpTest, usesCsrf, PostHttpSessionTest
import requests
import unittest
from django.conf import settings
loadTests = unittest.TestLoader().loadTestsFromTestCase


class ContactPage(GetHttpTest):
    """Perform a simple get request on the contact page to test html validity."""

    url = GetHttpTest.baseUrl + '/contact.html'
    testCodes = ['3a9f74ee-5c78-4ec0-8893-ce0476808131']


@usesCsrf
class PostContactPage(PostHttpSessionTest):
    """Perform a correctly formed POST request to the contact page to test html validity."""

    url = GetHttpTest.baseUrl + '/contact.html'

    def setUp(self):
        """Perform a correctly formed POST request to the contact page to test html validity."""
        self.response = self.s.post(self.url, data={'email': settings.ADMIN_EMAILS[
                                    0], 'content': 'This is a test message.', 'csrfmiddlewaretoken': self.csrf})


@usesCsrf
class PostContactPageBad(PostContactPage):
    """Perform a badly formed POST request to the contact page to test html validity."""

    status = 422

    def setUp(self):
        """Perform a badly formed POST request to the contact page to test html validity."""
        self.response = self.s.post(self.url, data={'email': settings.ADMIN_EMAILS[
                                    0], 'content': '', 'csrfmiddlewaretoken': self.csrf})


@usesCsrf
class PostContactPageBad2(PostContactPage):
    """Perform a badly formed POST request missing a field entirely to test html validity."""

    status = 422

    def setUp(self):
        """Perform a badly formed POST request missing a field entirely to test html validity."""
        self.response = self.s.post(
            self.url, data={'content': 'This is a test.', 'csrfmiddlewaretoken': self.csrf})


class PostContactPageBad3(PostContactPage):
    """Confirm that CSRF has been correctly implemented by forgetting the csrf token."""

    def setUp(self):
        """Confirm that CSRF has been correctly implemented by forgetting the csrf token."""
        self.response = requests.post(
            self.url, data={'content': 'This is a test.'})

    def test_Status(self):
        """Ensure that the response to a forgotten csrf token is a 403 error."""
        self.assertEqual(403, self.response.status_code)

suite = unittest.TestSuite([
    loadTests(ContactPage),
    loadTests(PostContactPage),
    loadTests(PostContactPageBad2),
    loadTests(PostContactPageBad3)
])

if __name__ == '__main__':
    # Runs the test- a good way to check that this particular test set works
    # without having to run all the tests.
    unittest.main()
