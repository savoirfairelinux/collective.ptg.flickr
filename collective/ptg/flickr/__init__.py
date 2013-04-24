
from zope import schema
from zope.interface import  Attribute, implements
from itertools import islice
from collective.plonetruegallery.interfaces import \
    IGalleryAdapter, IBaseSettings
    
from collective.plonetruegallery.galleryadapters.base import BaseAdapter

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('collective.plonetruegallery')

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

    flickr = Attribute("returns a flickrapi object for the api key")

    def get_flickr_user_id(username):
        """
        Returns the actual user id of someone given a username.
        if a username is not given, it will use the one in its
        settings
        """

    def get_flickr_api_key(username):
        """
        Returns the api key  (not sure if this is needed)
        """
        
    def get_flickr_api_secret(username):
        """
        Returns the api secret (not sure if this is needed)
        """
        
    def get_flickr_collection_id(self):
        """
        Returns the collection id. Uses value from settings.
        """

    def get_flickr_photoset_id(theset=None, userid=None):
        """
        Returns the photoset id given a set name and user id.
        Uses the set and get_flickr_user_id() if they are
        not specified.
        """

    def gen_collection_sets(user_id=None, collection_id=None):
        """
        Yields all photosets from a collection (as ElementTree objects)
        Available attributes: [id, title, description]
        """

    def gen_photoset_photos(user_id=None, photoset_id=None):
        """
        Yields all photos from a photoset (as ElementTree objects)
        Available attributes: ['secret', 'title', 'farm', 'isprimary', 'id', 'dateupload', 'server']
        """

    def gen_collection_photos(user_id=None, collection_id=None, max_photos=9999):
        """
        Yields all photos from given collection,
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
        title=_(u"label_flickr_username", default=u"flickr username"),
        description=_(u"description_flickr_username",
            default=u"The username/id of your flickr account. "
                    u"(*flickr* gallery type)"
        ),
        required=False)
    flickr_set = schema.TextLine(
        title=_(u"label_flickr_set", default=u"Flickr Set"),
        description=_(u"description_flickr_set",
            default=u"Name/id of your flickr set."
                    u"(*flickr* gallery type)"
        ),
        required=False)
        
    flickr_collection = schema.TextLine(
        title=_(u"label_flickr_collection", default=u"Collection ID"),
        description=_(u"description_flickr_collection",
            default=u"Will be ignored if a photoset is provided."),
        required=False)
        
    flickr_api_key = schema.TextLine(
        title=_(u"label_flickr_api_key", default="Flickr API key"),
        description=_(u"description_flickr_api_key",
            default=u"Your flickr api key."
                    u"(*flickr* gallery type)"
        ),
        default=u"9b354d88fb47b772fee4f27ab15d6854",
        required=False)
        
    
    flickr_api_secret = schema.TextLine(
        title=_(u"label_flickr_api_secret", default="Flickr API secret"),
        description=_(u"description_flickr_api_secret",
            default=u"Your flickr api secret."
                    u"(*flickr* gallery type)"
        ),
        required=False)

class FlickrAdapter(BaseAdapter):
    implements(IFlickrAdapter, IGalleryAdapter)

    schema = IFlickrGallerySettings
    name = u"flickr"
    description = _(u"label_flickr_gallery_type", default=u"Flickr")

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
        return settings.flickr_collection

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

    def gen_collection_photos(self, user_id, collection_id):

        # Collect every single photo from that collection.
        photos = []
        for photoset in self.gen_collection_sets(user_id, collection_id):
            photoset_id = photoset.attrib['id']
            for photo in self.gen_photoset_photos(user_id, photoset_id):
                photos.append(photo)

        # Most recent first.
        photos.sort(key=lambda p:p.attrib['dateupload'], reverse=True)

        # This could be a large list,
        # but the retrieve_images method will slice it.
        return iter(photos)


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
        '''
        Returns a FlickrAPI instance.
        API key and secret both come from settings interface.
        - self.settings.flickr_api_key
        - self.settings.flickr_api_secret
        '''
        return  flickrapi.FlickrAPI(self.settings.flickr_api_key)

    def retrieve_images(self):

        # These values are expected to be valid. We trust the user.
        user_id = self.get_flickr_user_id()
        photoset_id = self.get_flickr_photoset_id()
        collection_id = self.get_flickr_collection_id()

        photos = []

        if photoset_id:
            try:
                photos = self.gen_photoset_photos(user_id, photoset_id)
            except Exception, inst:
                self.log_error(Exception, inst, "Error getting all images")
                return []

        elif collection_id:
            try:
                photos = self.gen_collection_photos(user_id, collection_id)
            except Exception, inst:
                self.log_error(Exception, inst, "Error getting all images")
                return []


        # Slice iterator according to PloneTrueGallery's 'batch_size' setting.
        # We could also directly tell Flickr to send less photos but,
        # since PTG keeps a photo cache anyway, it's a bit overkill.
        if self.settings.batch_size:
            photos = islice(photos, self.settings.batch_size)

        return [self.assemble_image_information(image)
                for image in photos]

