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

    def authenticate(self):
        '''Test if the current user is authenticated.'''
        client = self._get_client_for_current_user()
        return client.authenticate()

    def get_email_address(self):
        '''Returns the email address of the current user.'''
        member = api.user.get_current()
        email = member.getProperty('email', '')
        return email

    def searchConversations(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.searchConversations(**query)

    def searchMessages(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.searchMessages(**query)

    def searchTasks(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.searchTasks(**query)

    def get_messages(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.searchMessages(**query)

    def get_message(self, eid):
        ''' '''
        client = self._get_client_for_current_user()
        return client.getMessage(id=eid, html='1')

    def get_conversations(self, **query):
        ''' '''
        client = self._get_client_for_current_user()
        return client.searchConversations(**query)

    def get_conversation(self, eid):
        ''' '''
        client = self._get_client_for_current_user()
        return client.getConversation(id=eid, fetch='all', html='1')

    def get_address_book(self, offset=0, limit=100):
        ''' '''
        client = self._get_client_for_current_user()
        return client.get_address_book(offset, limit)

    def create_task(self, dct):
        ''' '''
        client = self._get_client_for_current_user()
        return client.create_task(dct)

    def get_search_folder(self, **query):
        '''Returns the list of folders for the current user.'''
        client = self._get_client_for_current_user()
        result = client.get_search_folder(**query)
        return result


zimbraUtilInstance = ZimbraUtil()
