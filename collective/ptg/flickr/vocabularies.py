# from zope.component import getUtilitiesFor
# from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
# from collective.plonetruegallery.interfaces import IGallerySettings, IDisplayType
# from plone.app.vocabularies.catalog import SearchableTextSourceBinder
# from plone.app.vocabularies.catalog import SearchableTextSource
# from plone.app.vocabularies.catalog import parse_query
# from collective.plonetruegallery.interfaces import IGallery
# from Products.CMFCore.utils import getToolByName

from collective.plonetruegallery import PTGMessageFactory as _
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


def SizeVocabulary(context):

    # PTG default
    image_terms = [
        SimpleTerm('ptg_default', 'ptg_default', _(u"label_ptg_default",
                                        default=u'PTG default')),
    ]

    # Append Flickr size array from __init__.py
    from __init__ import FlickrAdapter
    sizes = FlickrAdapter.sizes['flickr'].keys()
    sizes.sort()
    for s in sizes:
        image_terms.append(SimpleTerm(s, s, s))

    return SimpleVocabulary(image_terms)
