from zope.interface import implements
from Products.CMFPlone.utils import safe_unicode as su
from plone.memoize.instance import memoize

from plone import api

from vnccollab.zimbra.interfaces import IZimbraUtil
from vnccollab.zimbra.zimbraclient import ZimbraUtilClient


class ZimbraUtil:
    """Zimbra Utility."""
    implements(IZimbraUtil)

    def _get_server_url(self):
        url = api.portal.get_registry_record('vnccollab.zimbra.server_url')
        return url

    def _get_credentials(self):
        member = api.user.get_current()
        username = member.getProperty('zimbra_username', '')
        password = member.getProperty('zimbra_password', '')
        # password could contain non-ascii chars, ensure it's properly encoded
        return username, su(password).encode('utf-8')

    @memoize
    def _get_client(self, url, username='', password=''):
        client = ZimbraUtilClient(url, username, password)
        return client

    def _get_client_for_current_user(self):
        url = self._get_server_url()
        username, password = self._get_credentials()
        return self._get_client(url, username, password)

    def search(self, query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.search(query)

    def get_raw_emails(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_raw_emails(**query)

    def get_emails(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_emails(**query)

    def get_email(self, eid):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_email(eid)

    def get_email_thread(self, eid):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_email_thread(eid)

    def get_address_book(self, offset=0, limit=100):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_address_book(offset, limit)

    def get_tasks(self):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_tasks()

    def create_task(self, dct):
        ''' '''
        client = self._get_client_for_current_user()
        return client.create_task(dct)


zimbraUtilInstance = ZimbraUtil()
