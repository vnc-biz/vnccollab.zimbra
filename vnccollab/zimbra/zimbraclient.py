import urlparse
from pyzimbra.soap import SoapException
from pyzimbra.auth import AuthException
from pyzimbra.z.client import ZimbraClient

from vnccollab.zimbra.content import Message, Conversation, Folder


def refreshAuthToken(func, *args, **kw):
    """Catches SoapException from passed function call and if the error is
    identified as Token Expiration error - authenticate client and then repeat
    the call.
    """
    def decorated(*args, **kw):
        try:
            result = func(*args, **kw)
        except SoapException, e:
            msg = unicode(e)
            if u'auth credentials have expired' in msg or \
               u'AUTH_EXPIRED' in msg:
                # authenticate, args[0] is func's method object
                args[0].authenticate()
                return func(*args, **kw)
            else:
                raise e
        else:
            return result

    return decorated


class ZimbraUtilClient:
    '''
    Zimbra client support class.

    It returns ZimbraClient results in a way more digerible by plone.
    '''
    def __init__(self, server_url, username='', password=''):
        # we must sanitize server url before generating self.url
        p = urlparse.urlparse(server_url)
        self.server_url = '{0}://{1}'.format(p.scheme, p.netloc)
        self.server_url = server_url
        self.url = self.server_url + '/service/soap'
        self.client = ZimbraClient(self.url)
        self.username = username
        self.password = password
        self.authenticated = False
        self.authenticate()

    def authenticate(self):
        if self.username:
            try:
                self.client.authenticate(self.username, self.password)
                self.authenticated = True
            except AuthException:
                self.authenticated = False
        else:
            self.authenticated = False

        return self.authenticated

    @refreshAuthToken
    def _invoke(self, command, query):
        result = self.client.invoke('urn:zimbraMail', command, query)
        # if pyzimbra has activated returnAllAttrs, result is a tuple.
        # We're interested here only in its first element
        if type(result) == tuple:
            result = result[0]

        return result

    def searchRequest(self, klass=None, folder=None,
                      searchable_text=None, **query):
        '''Returns the raw result of  SearchRequest.

        Args:
            klass: Class to convert the results.
            query: Dictionary with the query. It allows the following keys:
                offset:
                limit:
                sortBy:
                types:
                recip="0"|"1":
                fetch="1|all|{id}":
                read="0|1":
                max:
                html="0|1":
                neuter="0|1":
                field:
                resultMode
                inDumpster="0|1"
        '''
        if folder:
            query['query'] = 'in:%s' % folder

        if searchable_text:
            query['query'] = searchable_text

        result = self._invoke('SearchRequest', query)

        if klass is not None:
            result = [klass(x) for x in result]
        return result

    def searchConversations(self, **query):
        query['types'] = 'conversation'
        result = self.searchRequest(Conversation, **query)
        return result

    def searchMessages(self, **query):
        query['type'] = 'message'
        result = self.searchRequest(Message, **query)
        return result

    def searchTasks(self, **query):
        query['type'] = 'task'
        result = self.searchRequest(**query)
        return result

    def getItemRequest(self, klass=None, **query):
        '''
        '''
        result = self._invoke('GetItemRequest', query)
        if klass is not None:
            result = klass(result)
        return result

    def getMessage(self, **query):
        '''Returns a message, given its id.
        Args:
            query:
                id: Message id.
                read="0|1": Mark as read.
                raw="0|1": Returns raw message.
                max: Limit length of body.
                html="0|1": Return defanged html.
                neuter="0|1": Neuter images.
                part:
                ridZ:
                needExp: Return group info.
        '''
        nquery = dict(m=query)
        result = self._invoke('GetMsgRequest', nquery)
        result = Message(result)
        return result

    def getConversation(self, **query):
        nquery = dict(c=query)
        result = self._invoke('GetConvRequest', nquery)
        result = Conversation(result)
        return result

    @refreshAuthToken
    def get_address_book(self, offset=0, limit=100):
        '''Returns the address book of the user.'''
        query = {
            'types': 'contact',
            'sortBy': 'nameAsc',
            'offset': offset,
            'limit': limit,
            'query': 'in:contacts'
        }
        result = self.raw_searchRequest(query)
        return result

    @refreshAuthToken
    def get_email(self, eid):
        """Returns email by given id.

        It also marks conversation as read.
        """
        result = self.client.invoke('urn:zimbraMail', 'GetConvRequest',
            {'c': {'id': eid, 'fetch': 'all', 'html': '1'}})[0].m

        # TODO: make zimbra conversation as read
        if not isinstance(result, list):
            result = [result]

        return result

    @refreshAuthToken
    def create_task(self, dct):
        """Creates a task, given its description as a dictionary"""
        task = dict(**dct)
        for k, v in task.items():
            if v is None:
                task[k] = u''
        task['startDate'] = self._stringFromDate(task['startDate'])
        task['endDate'] = self._stringFromDate(task['endDate'])

        query = {
            'm': {
              #'l' : '24486', # List id. It could be ommited
              'inv': {
                'comp': {
                  'name': task.get('subject', ''),
                  'loc': task.get('location', ''),
                  'percentComplete': task.get('percentComplete', '0'),
                  'status': task.get('status', 'NEED'),    # Not started
                  'priority': task.get('priority', '5'),   # Normal
                  'or': {'a': task['author'],              # Required
                         'd': task.get('authorName', ''),
                  },
                },
              },
              'mp': {
                'ct': 'multipart/alternative',
                'mp': {
                    'ct': 'text/plain',
                    'content': task.get('content', '')}},
            }
        }
        if task['content']:
            query['m']['mp'] = {'ct': 'text/plain',
                                'content': task['content']}
        if task['startDate']:
            query['m']['inv']['comp']['s'] = {'d': task['startDate']}
        if task['endDate']:
            query['m']['inv']['comp']['e'] = {'d': task['endDate']}

        response, _ = self.client.invoke('urn:zimbraMail',
                'CreateTaskRequest', query)
        response = self._get_message(response._getAttr(u'invId'))
        task = self._taskFromGetMsgResponse(response)
        return task

    def get_search_folder(self, **query):
        '''Returns the list of folders for the current user.'''
        response, _ = self.client.get_search_folder_request(methodattrs=query)
        folders = Folder(response)
        return folders

    @refreshAuthToken
    def _get_message(self, id):
        '''Returns a message (mail, task, etc), given its id.'''
        query = {"_jsns": "urn:zimbraMail",
                 "m": {'id': id, 'html': 1, 'needExp': 1, 'max': 250000}}
        response, attrs = self.client.invoke('urn:zimbraMail',
                'GetMsgRequest', query)
        return response

    @refreshAuthToken
    def get_all_tasks(self):
        '''Returns all the zimbra tasks of the authenticated user.'''
        query = {'query': 'in:"tasks"', 'types': 'task', }
        response, _ = self.client.invoke('urn:zimbraMail',
                'SearchRequest', query)
        if type(response) != list:
            response = [response]
        return [self._taskFromSearchResponse(x) for x in response]

    def _taskFromGetMsgResponse(self, response):
        '''Returns a ZimbraTask given a zimbra CreateTaskResponse.'''
        id = response._getAttr('_orig_id')
        title = response.inv.comp._getAttr('name')
        body = getattr(response.inv.comp, 'fr', u'')
        return ZimbraTask(id, title, self.server_url, body)

    def _taskFromSearchResponse(self, response):
        '''Returns a ZImbraTask given a zimbra SearchResponse.'''
        id = response._getAttr('invId')
        title = response._getAttr('name')
        body = getattr(response, 'fr', u'')
        return ZimbraTask(id, title, self.server_url, body)

    def _stringFromDate(self, date=None):
        if not date:
            return ''
        return date.strftime('%Y%m%d')


class ZimbraTask:
    def __init__(self, id, title, server_url, body):
        self.id = id
        self.title = title
        self.server_url = server_url
        self.url = ('{0}/zimbra/h/search?su=1&si=0&so=0&sc=4&st=task'
              + '&id={1}&action=edittask').format(self.server_url, id)
        self.body = body

    def __eq__(self, other):
        return (self.id == other.id) and (self.server_url == other.server_url)

    def __repr__(self):
        if len(self.body) < 10:
            body = repr(self.body)
        else:
            body = repr(self.body[:10] + '...')
        return 'ZimbraTask({0}, {1}, {2})'.format(repr(self.id),
                repr(self.title), body)
