import requests
from urlparse import urlparse
from requests.auth import HTTPBasicAuth

from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.view import memoize

from vnccollab.zimbra import messageFactory as _
from vnccollab.zimbra.interfaces import IZimbraUtil


class ZimbraCalendarView(BrowserView):
    """Proxy View For Zimbra Calendar.

    This view uses requests to get zimbra's calendar page. In this way we
    can detect if there was a network error and produce a better error page.
    """
    _template = ViewPageTemplateFile('templates/calendar.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.base_url = ''
        self.url = request.get('url', '')
        if self.url:
            self.base_url = urlparse(self.url).netloc

    def __call__(self):
        return self._template()

    def getPageInfo(self):
        "Gets zimbra calendar html or an error message"
        if not self.url:
            return _('Missing Calendar URL'), ''

        error = self.check_credentials()
        if error:
            return error, ''

        zimbraUtil = getUtility(IZimbraUtil)
        username, password = zimbraUtil._get_credentials()
        response = requests.get(self.url,
                                auth=HTTPBasicAuth(username, password))

        if response.status_code != 200:
            return 'Network error %s' % response.status_code, ''

        html = self._add_base_url(response.text)
        return None, html

    def _add_base_url(self, html):
        """Adds a base tag to zimbra calendar page."""
        new_head = '<head>\n  <base href="https://%s">\n' % self.base_url
        return html.replace('<head>', new_head)

    def check_credentials(self):
        "Verifies the current user zimbra credetials. error='' if Ok."
        zimbraUtil = getUtility(IZimbraUtil)
        username, password = zimbraUtil._get_credentials()

        lost_keys = []
        if not username:
            lost_keys.append(_(u'zimbra_username'))
        if not password:
            lost_keys.append(_(u'zimbra_password'))

        error = ''
        if lost_keys:
            error = _(u"The calendar can't be shown, you need to configure "
                      u"the following fields: ")
            error = error + ', '.join(lost_keys)
            return error

        authenticated = zimbraUtil.authenticate()
        if not authenticated:
            error = _(u"There was a network error or the"
                      u" credentials for your zimbra account are incorrect.")
            return error

        return error
