

from zope.interface import Interface
from zope import schema
from five import grok
from Products.CMFCore.interfaces import ISiteRoot

from plone.z3cform import layout
from plone.directives import form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

class ISettings(form.Schema):
    """ Define settings data structure """

    api_key = schema.TextLine(title=u"API key", description=u"")
    api_secret = schema.TextLine(title=u"API secret", description=u"")

class SettingsEditForm(RegistryEditForm):
    """
    Define form logic
    """
    schema = ISettings
    label = u"Plone True Gallery Flickr settings"

class SettingsView(grok.CodeView):
    """
    View which wraps the settings form using ControlPanelFormWrapper to a HTML boilerplate frame.
    """
    grok.name("ptg-flickr-settings")
    grok.context(ISiteRoot)
    def render(self):
        view_factor = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
        view = view_factor(self.context, self.request)
        return view()
