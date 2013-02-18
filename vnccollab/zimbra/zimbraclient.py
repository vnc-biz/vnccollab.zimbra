import urlparse
from pyzimbra.soap import SoapException
from pyzimbra.auth import AuthException
from pyzimbra.z.client import ZimbraClient

from Products.CMFPlone.utils import safe_unicode as su

from vnccollab.zimbra.content import Message

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

        if username:
            self.authenticate(username, password)
        else:
            self.username = ''
            self.password = ''

    def authenticate(self, username, password):
        self.username = username
        self.password = password

        if username:
            try:
                self.client.authenticate(self.username, self.password)
                self.authenticated = True
            except AuthException:
                self.authenticated = False
        else:
            self.authenticated = False

    @refreshAuthToken
    def search(self, query):
        '''Returns the result of making the given query.'''
        result = self.client.invoke('urn:zimbraMail', 'SearchRequest', query)
        # if we have activated returnAllAttrs, result is a tuple.
        # We're interested here only in its first element
        if type(result) == tuple:
            result = result[0]

        # Get the result out of the list
        if not isinstance(result, list):
            result = [result]

        return result

    @refreshAuthToken
    def get_raw_emails(self, folder=None, searchable_text='',
                   offset=0, limit=10,
                   recip='1', sortBy='dateDesc', types='conversation'):
        """Returns list of email conversations.

        Args:
          @folder - if given, return list of emails from inside this folder
          @serchable_text - Text the email should have to be shown.
          @offset - if given, return list of emails starting from start
          @limit - return 'limit' number of emails
          @recip - whether to return 'to' email adress instead of 'from' for
                   sent messages and conversations
          @sort_by - sort result set by given field
        """
        query = {
            'types': types,
            'limit': limit,
            'offset': offset,
            'recip': recip,
            'sortBy': sortBy,
        }

        if folder:
            query['query'] = 'in:%s' % folder

        if searchable_text:
            query['query'] = searchable_text

        result = self.search(query)
        return result

    @refreshAuthToken
    def get_emails(self, folder=None, searchable_text='',
                   offset=0, limit=10,
                   recip='1', sortBy='dateDesc', types='conversation'):
        result = self.get_raw_emails(folder=folder,
                searchable_text=searchable_text, offset=offset, limit=limit,
                recip=recip, sortBy=sortBy, types=types)
        return [Message(x) for x in result]

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
        result = self.search(query)
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
    def get_email_thread(self, eid):
        """Returns conversation emails by given id.

        It also marks conversation as read.
        """
        result = self.get_email(eid)

        thread = []
        for item in result:
            from_ = [su(e._getAttr('p')) for e in item.e
                        if e._getAttr('t') == 'f']
            from_ = from_[0] if len(from_) else ''
            to = u', '.join([su(e._getAttr('d')) for e in item.e
                        if e._getAttr('t') == 't'])

            thread.append({
                'from': from_,
                'to': to,
                'body': item,
                'id': item._getAttr('_orig_id'),
                'date': item._getAttr('d'),
            })

            return thread

    def _dict_from_mail(self, mail):
        """Converts a zimbra mail into a dictionary"""
        people = mail.e
        if not people:
            people = []
        elif not isinstance(people, list):
            people = [people]

        # prepare subject
        subject = getattr(mail, 'su', '') or 'No Subject'

        dct = {
            'subject': su(subject),
            'body': u'%s (%s) - %s - %s' % (u', '.join([p._getAttr('d')
                    for p in people]), mail._getAttr('n'), su(mail.su),
                    su(getattr(mail, 'fr', ''))),
            'unread': u'u' in (mail._getAttr('f') or ''),
            'id': mail._getAttr('_orig_id'),
            'date': mail._getAttr('d'),
            'cid': mail._getAttr('cid'),
        }
        return dct

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
