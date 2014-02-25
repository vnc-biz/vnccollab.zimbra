import requests
from urlparse import urlparse
from requests.auth import HTTPBasicAuth

from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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
        self.base_rel_url = request.get('url', '')
        if self.base_rel_url:
            self.base_url = urlparse(self.base_rel_url).netloc

    def __call__(self):
        return self._template()

    def getPageInfo(self):
        "Gets zimbra calendar html or an error message"
        if not self.base_rel_url:
            return _('Missing Calendar URL'), ''

        error = self.check_credentials()
        if error:
            return error, ''

        zimbraUtil = getUtility(IZimbraUtil)
        username, password = zimbraUtil._get_credentials()
        response = requests.get(self.base_rel_url,
                                auth=HTTPBasicAuth(username, password))

        if response.status_code != 200:
            return 'Network error %s' % response.status_code, ''

        html = self._fix_calendar_html(response.text)
        return None, html

    def _fix_calendar_html(self, html):
        """Adds a base tag to zimbra calendar page."""
        new_head = '<head>\n  <base href="https://%s">\n' % self.base_url
        new_href = ' href="' + self.base_rel_url + '?'

        html = html.replace('<head>', new_head)
        html = html.replace(' href="?', new_href)
        return html

    def check_credentials(self):
        "Verifies the current user zimbra credetials. error='' if Ok."
        zimbraUtil = getUtility(IZimbraUtil)
        return zimbraUtil.check_credentials()
