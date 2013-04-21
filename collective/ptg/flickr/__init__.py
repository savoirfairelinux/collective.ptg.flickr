

# Zope imports
import zope.component
from z3c.form import validator
from zope.interface import implements
from zope.i18nmessageid import MessageFactory

# PTG imports
from collective.plonetruegallery.galleryadapters.base import BaseAdapter
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.validators import Data
from collective.plonetruegallery.interfaces import IGalleryAdapter

# local imports
from interfaces import IFlickrGallerySettings, IFlickrAdapter

_ = MessageFactory('collective.ptg.flickr')

# TODO : this should be a Plone setting
API_KEY = "9b354d88fb47b772fee4f27ab15d6854"

# TODO : this should be taken from PloneTrueGallery settings
MAX_COLLECTION_PHOTOS = 12

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

            # This means we're using a collection, not a set.
            if theset is None:
                return None

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

        # TODO : log "exception" here ?

        return None

    def get_flickr_collection_id(self):
        settings = self.settings
        return settings.flickr_collection.strip()

    def gen_collection_sets(self, user_id, collection_id):

        flickr = self.flickr

        # Yield all photosets.
        # Exception handling is expected to be made by calling context.
        for photoset in flickr \
            .collections_getTree(
                        user_id=user_id,
                        collection_id=collection_id) \
            .find('collections') \
            .find('collection').getchildren(): yield photoset

    def gen_photoset_photos(self, user_id, photoset_id):

        flickr = self.flickr

        # Yield all photos.
        # Exception handling is expected to be made by calling context.
        for photo in flickr \
                    .photosets_getPhotos(
                            user_id=user_id,
                            photoset_id=photoset_id,
                            extras='date_upload',
                            media='photos') \
                    .find('photoset').getchildren(): yield photo

    def get_collection_photos(self, user_id, collection_id, max_photos=MAX_COLLECTION_PHOTOS):

        # Collect every single photo from that collection.
        photos = []
        for photoset in self.gen_collection_sets(user_id, collection_id):
            photoset_id = photoset.attrib['id']
            for photo in self.gen_photoset_photos(user_id, photoset_id):
                photos.append(photo)

        # Most recent first.
        photos.sort(key=lambda p:p.attrib['dateupload'], reverse=True)

        # We really don't need them all.
        return photos[:max_photos]


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

        user_id = self.get_flickr_user_id()
        photoset_id = self.get_flickr_photoset_id()
        collection_id = self.get_flickr_collection_id()

        if photoset_id:

            try:
                photos = self.gen_photoset_photos(user_id, photoset_id)
            except Exception, inst:
                self.log_error(Exception, inst, "Error getting all images")
                return []
            else:
                return [self.assemble_image_information(image) for image in photos]

        elif collection_id:

            try:
                photos = self.get_collection_photos(user_id, collection_id)
            except Exception, inst:
                self.log_error(Exception, inst, "Error getting all images")
                return []
            else:
                return [self.assemble_image_information(image) for image in photos]

        # TODO : will this ever happen ?
        else: return []


class FlickrSetValidator(validator.SimpleFieldValidator):

    def validate(self, photoset):
        super(FlickrSetValidator, self).validate(photoset)

        context = self.context
        request = self.request
        settings = Data(self.view)

        if settings.gallery_type != 'flickr':
            return

        adapter = getGalleryAdapter(context, request, settings.gallery_type)
        user_id = adapter.get_flickr_user_id(settings.flickr_username)
        collection_id = adapter.get_flickr_collection_id()

        if empty(photoset) and empty(collection_id):
            raise zope.schema.ValidationError(
                _(u"Please provide a Flickr set to use."),
                True
            )

        try:
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

        adapter = getGalleryAdapter(context, request, settings.gallery_type)
        user_id = adapter.get_flickr_user_id()

        try:
            # Failure to obtain the collection's first photoset
            # means it's nonexistent or empty
            adapter.gen_collection_sets(
                    user_id=user_id,
                    collection_id=collection_id).next()

        # TODO : specific exception handling; adapter.flickr.FlickrError...
        except:
            raise zope.schema.ValidationError(
                _(u"Could not find collection, or collection is empty."),
                True
            )


validator.WidgetValidatorDiscriminators(FlickrCollectionValidator,
    field=IFlickrGallerySettings['flickr_collection'])
zope.component.provideAdapter(FlickrCollectionValidator)

