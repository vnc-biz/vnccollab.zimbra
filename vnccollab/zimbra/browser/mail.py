import types
import simplejson
from Acquisition import aq_inner
from BeautifulSoup import BeautifulSoup

from zope.component import getUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFPlone.utils import safe_unicode as su

from plone.memoize.instance import memoize
from plone.portlets.utils import unhashPortletInfo
from plone.app.portlets.utils import assignment_mapping_from_key

from vnccollab.zimbra import messageFactory as _
from vnccollab.zimbra.content import EmailAddress
from vnccollab.zimbra.interfaces import IZimbraUtil
from vnccollab.zimbra.portlets.zimbra_mail import Renderer


class ZimbraMailPortletView(BrowserView):
    """High level Zimbra Mail Portlet view to communicate with Zimbra SOAP API.

    It uses pyzimbra and SOAPpy.
    """

    _emails_template = ZopeTwoPageTemplateFile(
        'templates/zimbra_emails_template.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.client = getUtility(IZimbraUtil)

    def view_name(self):
        """To refer to itself in a bit more generic way"""
        return self.__name__

    def __call__(self, action, portlethash):
        """Main method that accepts action to perform.

        Args:
          @action - one of allowed actions, like emails, create, send, etc...
          @portlethash - portlet hash so we get portlet assignement data.

        This method accepts only post requests.
        It returns json.
        It authenticates before any further actions.
        """
        # check if method is POST
        request = self.request
        if request.method != 'POST':
            return self._error(_(u"Request method is not allowed."))

        # check if action is valid
        if action not in ('emails', 'email'):
            return self._error(_(u"Requested action is not allowed."))

        mails = []
        if action == 'emails':
            mails = self.get_emails(
                request.get('folder') or None,
                int(request.get('offset') or '0'),
                int(request.get('limit') or '100'),
                request.get('recip') or '1',
                request.get('sortBy') or 'dateDesc'
            )

        elif action == 'email':
            mails = self.get_email(request.get('eid'))

        return simplejson.dumps(mails)

    def _error(self, msg):
        return simplejson.dumps({'error': msg})

    def get_emails(self, folder=None, offset=0, limit=10, recip='1',
                   sortBy='dateDesc'):
        """Returns list of email conversations.

        Args:
          @folder - if given, return list of emails from inside this folder
          @offset - if given, return list of emails starting from start
          @limit - return 'limit' number of emails
          @recip - whether to return 'to' email adress instead of 'from' for
                   sent messages and conversations
          @sort_by - sort result set by given field
        """
        emails = self.client.get_conversations(folder=folder, offset=offset,
                                               limit=limit, recip=recip,
                                               sortBy=sortBy)
        return {'emails': self._emails_template(emails=emails).encode('utf-8')}

    def get_email(self, eid):
        """Returns conversation emails by given id.

        It also marks conversation as read.
        """
        if not eid:
            return {'error': _(u"Conversation id is not valid.")}

        conversation = self.client.get_conversation(eid)
        thread = []
        for message in conversation.messages:
            from_ = _name(message, EmailAddress.FROM)

            if len(from_):
                from_ = 'from: ' + from_[0]
            else:
                from_ = ''

            to = u', '.join(_mail(message, EmailAddress.TO))

            soup = BeautifulSoup(findMsgBody(message.raw))
            [elem.decompose() for elem in soup.findAll(['script', 'style'])]

            for tag in soup():
                for attribute in ['style']:
                    del tag[attribute]
                if tag.name in ['html', 'head', 'body']:
                    tag.append(' ')
                    tag.replaceWithChildren()

            thread.append({
                'from': '<div class="item-from">' + from_ + '</div>',
                'to': to,
                'body': ''.join(unicode(soup)),
                'id': message.original_id,
                'date': message.date,
            })

        return {'conversation': ''.join([t['from'] + '<div class="item-thread">' + t['body'] + '</div>'
            for t in thread])}

    def create_email(self):
        return None

    def display_name(self, conversation):
        addresses = conversation.addresses
        if addresses:
            return addresses[0].display_name
        else:
            return ''

    @memoize
    def _data(self, portlethash):
        """Returns zimbra mail related settings based on portlet assignment
        object and currently logged in user.
        """
        context = aq_inner(self.context)
        info = unhashPortletInfo(portlethash)
        assignment = assignment_mapping_from_key(context,
                                                 info['manager'],
                                                 info['category'],
                                                 info['key'])[info['name']]
        renderer = Renderer(context, self.request, self, None, assignment)
        username, password = renderer.getAuthCredentials()
        return {
            'url': assignment.url,
            'folder_id': assignment.folder_id,
            'emails_limit': assignment.count,
            'username': username,
            'password': password
        }


def findMsgBody(node, format='text/html'):
    """Recursively goes over attachments and finds body"""
    if hasattr(node, '_name') and node._name == 'mp' and \
       hasattr(node, '_getAttr') and node._getAttr('body') == '1' and \
       node._getAttr('ct') == format and hasattr(node, 'content'):
        return su(node.content)

    if hasattr(node, 'mp'):
        mp = node.mp
        if not isinstance(mp, (types.ListType, types.TupleType)):
            mp = [mp]
        for sub_node in mp:
            body = findMsgBody(sub_node, format)
            if body:
                return body

    return u''


def _mail(message, type):
    mails = message.filter_addresses(type)
    result = [x.email_address for x in mails]
    return result


def _name(message, type):
    mails = message.filter_addresses(type)
    result = [x.personal_name for x in mails]
    return result

