
# Zope imports
from z3c.form import validator
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Attribute
import zope.component

# PTG imports
from collective.plonetruegallery.interfaces import IGalleryAdapter, IBaseSettings

# Local imports
from validators import (
        FlickrUserValidator,
        FlickrSetValidator,
        FlickrCollectionValidator)

# Translation
_ = MessageFactory('collective.ptg.flickr')


class IFlickrAdapter(IGalleryAdapter):
    """
    """

    flickr = Attribute("Returns a flickrapi object for the api key")

    def get_flickr_user_id(username):
        """
        Returns the actual user id of someone given a username.
        if a username is not given, it will use the one in its
        settings
        """

    def get_flickr_photoset_id(user_id=None, theset=None):
        """
        Returns the photoset id given a set name and user id.
        Uses the set and get_flickr_user_id() if they are
        not specified.
        """

    def get_flickr_collection_id(self):
        """
        Returns the collection id. Uses value from settings.
        """

    def gen_collection_sets(user_id=None, collection_id=None):
        """
        Yields all photosets from a collection (as ElementTree objects)
        Available attributes: [id, title, description]

        Uses values from settings if user_id and collection_id are not specified.
        """

    def gen_photoset_photos(user_id=None, photoset_id=None):
        """
        Yields all photos from a photoset (as ElementTree objects)
        Available attributes: ['secret', 'title', 'farm', 'isprimary', 'id', 'dateupload', 'server']

        Uses values from settings if user_id and photoset_id are not specified.
        """

    def get_collection_photos(user_id=None, collection_id=None, max_photos=9999):
        """
        Returns a sliced list of photos from given collection,
        sorted by upload date (most recent first)

        Available attributes: same as gen_photoset_photos.
        """

    def get_mini_photo_url(photo):
        """
        takes a photo and creates the thumbnail photo url
        """

    def get_photo_link(photo):
        """
        creates the photo link url
        """

    def get_large_photo_url(photo):
        """
        create the large photo url
        """

class IFlickrGallerySettings(IBaseSettings):

    flickr_username = schema.TextLine(
        title=_(u"Flickr username or ID"),
        required=False)

    flickr_set = schema.TextLine(
        title=_(u"Photoset title or ID"),
        description=_(u"Has priority over collection."),
        required=False)

    flickr_collection = schema.TextLine(
        title=_("Collection ID"),
        description=_(u"Will be ignored if a photoset is provided."),
        required=False)

# Validators for IFlickrGallerySettings

validator.WidgetValidatorDiscriminators(FlickrUserValidator,
    field=IFlickrGallerySettings['flickr_username'])
zope.component.provideAdapter(FlickrUserValidator)

validator.WidgetValidatorDiscriminators(FlickrSetValidator,
    field=IFlickrGallerySettings['flickr_set'])
zope.component.provideAdapter(FlickrSetValidator)

validator.WidgetValidatorDiscriminators(FlickrCollectionValidator,
    field=IFlickrGallerySettings['flickr_collection'])
zope.component.provideAdapter(FlickrCollectionValidator)

