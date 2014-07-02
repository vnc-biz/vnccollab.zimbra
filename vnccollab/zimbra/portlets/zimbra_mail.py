import sys
import logging

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getUtility

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from vnccollab.zimbra import messageFactory as _
from vnccollab.zimbra.interfaces import IZimbraUtil

MYLOGGER = logging.getLogger('vnccollab.zimbra.ZimbraMailPortlet')


def logException(msg, context=None, logger=MYLOGGER):
    logger.exception(msg)
    if context is not None:
        error_log = getattr(context, 'error_log', None)
        if error_log is not None:
            error_log.raising(sys.exc_info())


class IZimbraMailPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Header of the portlet."),
        required=True,
        default=u'Zimbra Mail')

    url = schema.URI(
        title=_(u"Zimbra service URL"),
        description=_(u"Root url to your Zimbra service."),
        required=True,
        default='https://')

    folder_id = schema.ASCIILine(
        title=_(u"Mail Folder Id"),
        description=_(u"The name of the mail folder to access. This can be a "
                      "default or a user-defined folder. Default folders "
                      "include: inbox, drafts, sent, trash, junk."),
        required=True,
        default='inbox')

    count = schema.Int(
        title=_(u"Number of items to display"),
        description=_(u"How many items to list."),
        required=True,
        default=5)

    username = schema.ASCIILine(
        title=_(u"Username"),
        description=_(u"If not set, zimbra_username property of authenticated "
                      "user will be used."),
        required=False,
        default='')

    password = schema.Password(
        title=_(u"Password"),
        description=_(u"If not set, zimbra_password property of authenticated "
                      "user will be used."),
        required=False,
        default=u'')

    timeout = schema.Int(
        title=_(u"Data reload timeout"),
        description=_(u"Time in minutes after which the data should be "
                      u" reloaded from Zimbra service. Minimun value:"
                      u" 1 minute."),
        required=True,
        default=5,
        min=1)

    request_timeout = schema.Int(
        title=_(u"Request timeout"),
        description=_(u"How many seconds to wait for hanging Zimbra request."),
        required=True,
        default=15)

    failure_delay = schema.Int(
        title=_(u"Failure delay"),
        description=_(u"Time in minutes before retry to load data from Zimbra "
                      "after a failure"),
        required=True,
        default=5)


class Assignment(base.Assignment):
    implements(IZimbraMailPortlet)

    header = u'Zimbra Mail'
    protocol = 'https://'
    url = 'https://'
    folder_id = 'inbox'
    count = 5
    username = ''
    password = u''
    timeout = 5
    request_timeout = 15
    failure_delay = 5

    @property
    def title(self):
        """Return portlet header"""
        return self.header

    def __init__(self, header=u'', url='https://',
                 folder_id='inbox', count=5, username='', password=u'',
                 timeout=5, request_timeout=15, failure_delay=5):
        self.header = header
        self.url = url
        self.folder_id = folder_id
        self.count = count
        self.username = username
        self.password = password
        self.timeout = timeout
        self.request_timeout = request_timeout
        self.failure_delay = failure_delay


class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('templates/zimbra_mail.pt')

    def update(self):
        pass

    def check_credentials(self):
        """Returns an error message is the user credentials are no ok."""
        zimbraUtil = getUtility(IZimbraUtil)
        return zimbraUtil.check_credentials()

    @memoize
    def getAuthCredentials(self):
        """Returns username and password for zimbra user."""
        username, password = self.data.username, self.data.password
        if not (username and password):
            # take username and password from authenticated user Zimbra creds
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            username, password = member.getProperty('zimbra_username', ''), \
                member.getProperty('zimbra_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, safe_unicode(password).encode('utf-8')

    @property
    def title(self):
        """return title of feed for portlet"""
        return self.data.header

    @property
    def folders(self):
        client = getUtility(IZimbraUtil)
        try:
            folders = client.get_search_folder()
        except :
            return []

        folders = [x for x in _flat_folders(folders) if x.type == 'message']
        info = [(x.absFolderPath, x.absFolderPath, x.name == 'Inbox')
                for x in folders]
        return info


def _flat_folders(folder, lst=None):
    if lst is None:
        lst = []
    lst.append(folder)
    for sub in folder.folders:
        lst = _flat_folders(sub, lst)
    return lst


class AddForm(base.AddForm):
    form_fields = form.Fields(IZimbraMailPortlet)
    label = _(u"Add Zimbra Mail Portlet")
    description = _(u"This portlet allows managing Zimbra Mail box.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IZimbraMailPortlet)
    label = _(u"Edit Zimbra Mail Portlet")
    description = _(u"This portlet allows managing Zimbra Mail box.")
