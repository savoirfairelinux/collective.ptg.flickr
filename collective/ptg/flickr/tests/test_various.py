from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility

from collective.ptg.flickr import IFlickrGallerySettings
from collective.ptg.galleria import IGalleriaDisplaySettings
from collective.plonetruegallery.tests import BaseTest

import unittest2 as unittest


class TestSettings(BaseTest):

    def test_should_set_setting_correctly(self):
        settings = GallerySettings(self.get_gallery())
        settings.gallery_type = "flickr"
        self.assertEquals(settings.gallery_type, "flickr")

    def test_should_set_extra_interface_setting(self):
        settings = GallerySettings(
            self.get_gallery(),
            interfaces=[IFlickrGallerySettings]
        )
        settings.flickr_username = "john"
        self.assertEquals(settings.flickr_username, "john")

