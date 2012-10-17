from z3c.form import validator, error
import zope.interface
import zope.component
import zope.schema
from collective.ptg.flickr.interfaces import IFlickrGallerySettings


class FlickrSetValidator(validator.SimpleFieldValidator):

    def validate(self, photoset):
        super(FlickrSetValidator, self).validate(photoset)
        settings = Data(self.view)

        if settings.gallery_type != 'flickr':
            return

        if empty(photoset):
            raise zope.schema.ValidationError(
                _(u"label_validate_flickr_specify_user",
                    default=u"You must specify a flickr set to use."),
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
                    _(u"label_validate_flickr_find_set",
                    default="Could not find flickr set."),
                    True
                )
        except:
            raise zope.schema.ValidationError(
                _(u"label_validate_flickr_find_set",
                default="Could not find flickr set."),
                True
            )
validator.WidgetValidatorDiscriminators(FlickrSetValidator,
    field=IFlickrGallerySettings['flickr_set'])
zope.component.provideAdapter(FlickrSetValidator)


class FlickrUsernameValidator(validator.SimpleFieldValidator):

    def validate(self, username):
        super(FlickrUsernameValidator, self).validate(username)

        settings = Data(self.view)
        if settings.gallery_type != 'flickr':
            return

        if empty(username):
            raise zope.schema.ValidationError(
                _(u"label_validate_flickr_specify_username",
                default=u"You must specify a username."),
                True
            )

        try:
            adapter = getGalleryAdapter(self.context, self.request,
                                        settings.gallery_type)
            flickr_userid = adapter.get_flickr_user_id(username)
            if empty(flickr_userid):
                raise zope.schema.ValidationError(
                    _(u"label_validate_flickr_user",
                    default=u"Could not find flickr user."),
                    True
                )
        except:
            raise zope.schema.ValidationError(_(u"label_validate_flickr_user",
                default=u"Could not find flickr user."),
                True
            )
validator.WidgetValidatorDiscriminators(FlickrUsernameValidator,
    field=IFlickrGallerySettings['flickr_username'])
zope.component.provideAdapter(FlickrUsernameValidator)


