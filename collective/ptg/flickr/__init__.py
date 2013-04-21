

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

    def get_flickr_photoset_id(user_id=None, theset=None):
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
        settings = self.settings
        flickr = self.flickr

        if username is None:
            username = settings.flickr_username
        username = username.strip()

        # Must be an username.
        try:
            return flickr \
                    .people_findByUsername(username=username) \
                    .find('user').get('nsid')

        # No ? Must be an ID then.
        except:
            try:
                return flickr \
                        .people_getInfo(user_id=username) \
                        .find('person').get('nsid')
            except Exception, inst:
                self.log_error(Exception, inst, "Can't find Flickr user ID")

        return None

    def get_flickr_photoset_id(self, user_id=None, theset=None):
        settings = self.settings
        flickr = self.flickr

        if user_id is None:
            user_id = self.get_flickr_user_id()
        user_id = user_id.strip()

        if theset is None:
            theset = settings.flickr_set
        theset = theset.strip()

        photosets = flickr \
                    .photosets_getList(user_id=user_id) \
                    .find('photosets').getchildren()

        for photoset in photosets:

            photoset_title = photoset.find('title').text
            photoset_id = photoset.get('id')

            # Matching title or ID means we found it.
            if theset in (photoset_title, photoset_id):
                return photoset_id

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

        flickr = self.flickr
        user_id = self.get_flickr_user_id()
        photoset_id = self.get_flickr_photoset_id()

        try:
            photos = flickr \
                    .photosets_getPhotos(
                            user_id=user_id,
                            photoset_id=photoset_id,
                            media='photos') \
                    .find('photoset').getchildren()

            return [self.assemble_image_information(image) for image in photos]
        except Exception, inst:
            self.log_error(Exception, inst, "Error getting all images")
            return []
            

class FlickrSetValidator(validator.SimpleFieldValidator):

    def validate(self, photoset):
        super(FlickrSetValidator, self).validate(photoset)
        context = self.context
        request = self.request
        settings = Data(self.view)

        if settings.gallery_type != 'flickr':
            return

        if empty(photoset):
            raise zope.schema.ValidationError(
                _(u"Please provide a Flickr set to use."),
                True
            )

        try:
            adapter = getGalleryAdapter(context, request, settings.gallery_type)
            user_id = adapter.get_flickr_user_id(settings.flickr_username)
            photoset_id = adapter.get_flickr_photoset_id(user_id, photoset)

            if empty(photoset_id):
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

        context = self.context
        request = self.request

        settings = Data(self.view)
        if settings.gallery_type != 'flickr':
            return

        if empty(username):
            raise zope.schema.ValidationError(
                _(u"You must specify a Flickr user ID."),
                True
            )

        try:
            adapter = getGalleryAdapter(context, request, settings.gallery_type)
            user_id = adapter.get_flickr_user_id(username)
            if empty(user_id):
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


class FlickrCollectionValidator(validator.SimpleFieldValidator):

    def validate(self, collection_id):
        super(FlickrCollectionValidator, self).validate(collection_id)
        context = self.context
        request = self.request
        settings = Data(self.view)

        if settings.gallery_type != 'flickr':
            return

        # Nothing to validate, and the field is not required.
        if empty(collection_id):
            return

        # TODO : validate it for real (work in progress)
        return

        raise zope.schema.ValidationError(
            _(u"Could not find flickr collection."),
            True
        )
validator.WidgetValidatorDiscriminators(FlickrCollectionValidator,
    field=IFlickrGallerySettings['flickr_collection'])
zope.component.provideAdapter(FlickrCollectionValidator)


