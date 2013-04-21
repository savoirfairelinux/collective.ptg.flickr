

# Zope imports
import zope.component
from z3c.form import validator
from zope import schema
from zope.interface import Attribute, implements

# PTG imports
from collective.plonetruegallery.galleryadapters.base import BaseAdapter
from collective.plonetruegallery.interfaces import IGalleryAdapter, IBaseSettings
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.validators import Data

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.flickr')

API_KEY = "9b354d88fb47b772fee4f27ab15d6854"

try:
    import flickrapi
except:
    pass


def add_condition():
    try:
        import flickrapi
    except:
        return False
    return True

def empty(v):
    return v is None or len(v.strip()) == 0

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

    def get_flickr_photoset_id(theset=None, userid=None):
        """
        Returns the photoset id given a set name and user id.
        Uses the set and get_flickr_user_id() if they are
        not specified.
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
        title=_(u"Flickr User"),
        description=_(u"The ID of your Flickr account."),
        required=False)

    flickr_set = schema.TextLine(
        title=_(u"Photoset"),
        description=_(u"The ID of your Flickr photoset."
                      u" Has priority over collection ID."),
        required=False)

    flickr_collection = schema.TextLine(
        title=_("Collection"),
        description=_(u"ID of your Flickr collection."
                      u" Will be ignored if a photoset ID is provided."
        ),
        required=False)

class FlickrAdapter(BaseAdapter):
    implements(IFlickrAdapter, IGalleryAdapter)

    schema = IFlickrGallerySettings
    name = u"flickr"
    description = _(u"Flickr")

    sizes = {
        'small': {
            'width': 500,
            'height': 375
        },
        'medium': {
            'width': 640,
            'height': 480
        },
        'large': {
            'width': 1024,
            'height': 768
        },
        'thumb': {
            'width': 72,
            'height': 72
        },
        'flickr': {
            'small': '_m',
            'medium': '',
            'large': '_b'
        }
    }

    def assemble_image_information(self, image):
        img_url = self.get_large_photo_url(image)
        return {
            'image_url': img_url,
            'thumb_url': self.get_mini_photo_url(image),
            'link': self.get_photo_link(image),
            'title': image.get('title'),
            'description': "",
            'original_image_url': img_url,
            'download_url': img_url,
            'copyright': '',
            'portal_type': '_flickr',
            'keywords': '', 
            'bodytext': ''
        }

    def get_flickr_user_id(self, username=None):
        if username is None:
            username = self.settings.flickr_username
        username = username.strip()

        try:
            return self.flickr.people_findByUsername(
                username=username).find('user').get('nsid')
        except:
            try:
                return self.flickr.people_getInfo(
                    user_id=username).find('person').get('nsid')
            except Exception, inst:
                self.log_error(Exception, inst, "Can't find Flickr user ID")

        return None

    def get_flickr_photoset_id(self, theset=None, userid=None):
        if userid is None:
            userid = self.get_flickr_user_id()
        userid = userid.strip()

        if theset is None:
            theset = self.settings.flickr_set
        theset = theset.strip()

        sets = self.flickr.photosets_getList(user_id=userid)

        for photoset in sets.find('photosets').getchildren():
            if photoset.find('title').text == theset or \
                    photoset.get('id') == theset:
                return photoset.get('id')

        return None

    def get_mini_photo_url(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (
            photo.get('farm'),
            photo.get('server'),
            photo.get('id'),
            photo.get('secret'),
        )

    def get_photo_link(self, photo):
        return "http://www.flickr.com/photos/%s/%s/sizes/o/" % (
            self.settings.flickr_username,
            photo.get('id')
        )

    def get_large_photo_url(self, photo):
        return "http://farm%s.static.flickr.com/%s/%s_%s%s.jpg" % (
            photo.get('farm'),
            photo.get('server'),
            photo.get('id'),
            photo.get('secret'),
            self.sizes['flickr'][self.settings.size]
        )

    @property
    def flickr(self):
        return  flickrapi.FlickrAPI(API_KEY)

    def retrieve_images(self):
        try:
            photos = self.flickr.photosets_getPhotos(
                user_id=self.get_flickr_user_id(),
                photoset_id=self.get_flickr_photoset_id(),
                media='photos'
            )

            return [self.assemble_image_information(image)
                for image in photos.find('photoset').getchildren()]
        except Exception, inst:
            self.log_error(Exception, inst, "Error getting all images")
            return []


            
            
class FlickrSetValidator(validator.SimpleFieldValidator):

    def validate(self, photoset):
        super(FlickrSetValidator, self).validate(photoset)
        settings = Data(self.view)

        if settings.gallery_type != 'flickr':
            return

        if empty(photoset):
            raise zope.schema.ValidationError(
                _(u"Please provide a Flickr set to use."),
                True
            )

        try:
            adapter = getGalleryAdapter(self.context, self.request,
                                        settings.gallery_type)
            userid = adapter.get_flickr_user_id(settings.flickr_username)
            flickr_photosetid = adapter.get_flickr_photoset_id(photoset,
                                                               userid)

            if empty(flickr_photosetid):
                raise zope.schema.ValidationError(
                    _(u"Could not find Flickr set."),
                    True
                )

        except:
            raise zope.schema.ValidationError(
                _(u"Could not find Flickr set."),
                True
            )
validator.WidgetValidatorDiscriminators(FlickrSetValidator,
    field=IFlickrGallerySettings['flickr_set'])
zope.component.provideAdapter(FlickrSetValidator)


class FlickrUserValidator(validator.SimpleFieldValidator):

    def validate(self, username):
        super(FlickrUserValidator, self).validate(username)

        settings = Data(self.view)
        if settings.gallery_type != 'flickr':
            return

        if empty(username):
            raise zope.schema.ValidationError(
                _(u"You must specify a Flickr user ID."),
                True
            )

        try:
            adapter = getGalleryAdapter(self.context, self.request,
                                        settings.gallery_type)
            flickr_userid = adapter.get_flickr_user_id(username)
            if empty(flickr_userid):
                raise zope.schema.ValidationError(
                    _(u"Could not find Flickr user."),
                    True
                )
        except:
            raise zope.schema.ValidationError(_(u"Could not find Flickr user."),
                True
            )
validator.WidgetValidatorDiscriminators(FlickrUserValidator,
    field=IFlickrGallerySettings['flickr_username'])
zope.component.provideAdapter(FlickrUserValidator)


