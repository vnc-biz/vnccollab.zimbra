from zope import schema
from zope.component import adapts
from zope.interface import implements, Interface
from zope.publisher.browser import IBrowserRequest

from collective.customizablePersonalizeForm.adapters.interfaces import \
    IExtendedUserDataSchema, IExtendedUserDataPanel

from vnccollab.zimbra import messageFactory as _


class UserDataSchemaAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataSchema)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getSchema(self):
        return IUserDataSchema


class UserDataSchemaPropertiesAdapter(object):
    adapts(object, IBrowserRequest)
    implements(IExtendedUserDataPanel)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getProperties(self):
        return ['zimbra_username', 'zimbra_password']


class IUserDataSchema(Interface):

    zimbra_username = schema.ASCIILine(
        title=_("Zimbra Username"),
        description=_(u"Zimbra username (without the '@' or domain). "
                      u"We need this field in order to display your Zimbra "
                      u"related information, like mail box, calendar, "
                      u"contacts, etc..."),
        required=False)

    zimbra_password = schema.Password(
        title=_("Zimbra Password"),
        description=_(u"We need this field in order to display your Zimbra "
                      u"related information, like mail box, calendar, "
                      u"contacts, etc..."),
        required=False)
