
# Zope imports
from z3c.form import validator
import zope.component
from zope.i18nmessageid import MessageFactory

# PTG imports
from collective.plonetruegallery.utils import getGalleryAdapter
from collective.plonetruegallery.validators import Data

# Translation
_ = MessageFactory('collective.ptg.flickr')


def empty(v):
    return v is None or len(v.strip()) == 0

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


