from DateTime import DateTime

from zope.interface import implements
from Products.CMFPlone.utils import safe_unicode

from vnccollab.zimbra.interfaces import IEmailAddress, IMessage


class EmailAddress:
    '''Zimbra Email.'''
    implements(IEmailAddress)

    '''Types of emails.'''
    FROM = 'f'
    TO = 't'
    CC = 'c'
    BCC = 'b'
    REPLY = 'r'
    SENDER = 's'
    NOTIFICATION = 'n'  # Read recipient notification

    def __init__(self, zimbra_email):
        self.type = _safe_get_attr(zimbra_email, 't')
        self.email_address = _safe_get_attr(zimbra_email, 'a')
        self.personal_name = _safe_get_attr(zimbra_email, 'p')
        self.display_name = _safe_get_attr(zimbra_email, 'd')
        self.content_name = _safe_get_node(zimbra_email, 'e')


class MIMEPart:
    '''MIME Part.'''
    def __init__(self, zimbra_part):
        self.raw = zimbra_part
        self.part_name = _safe_get_attr(zimbra_part, 'part')
        self.is_body = _get_attr(zimbra_part, 'body', False) == '1'
        self.size = int(_safe_get_attr(zimbra_part, 's', 0))
        self.message_id = _safe_get_attr(zimbra_part, 'mid')
        self.conversation_id = _safe_get_attr(zimbra_part, 'cid')
        self.truncated = _safe_get_attr(zimbra_part, 'truncated', False) == '1'
        self.content_type = _safe_get_attr(zimbra_part, 'ct')
        self.content_disposition = _safe_get_attr(zimbra_part, 'cd')
        self.filename = _safe_get_attr(zimbra_part, 'filename')
        self.content_id = _safe_get_attr(zimbra_part, 'ci')
        self.content_location = _safe_get_attr(zimbra_part, 'cl')
        self.content = _safe_get_node(zimbra_part, 'content')
        parts = _safe_get_node(zimbra_part, 'mp', [])

        if type(parts) != list:
            parts = [parts]

        self.parts = [MIMEPart(x) for x in parts if x]


class MessageBase:
    def __init__(self, zimbra_object):
        self.raw = zimbra_object
        self.id = _safe_get_attr(zimbra_object, 'id')
        self.flags = _safe_get_attr(zimbra_object, 'f')
        self.date = _date_from_zimbra_date(_safe_get_attr(zimbra_object, 'd'))
        self.subject = _safe_get_node(zimbra_object, 'su')
        self.fragment = _safe_get_node(zimbra_object, 'fr')
        self.addresses = self._addresses(_safe_get_node(zimbra_object,
                                                        'e', []))

    def filter_addresses(self, filter):
        return [email for email in self.addresses if email.type == filter]

    def _addresses(self, addressList):
        if type(addressList) != list:
            addressList = [addressList]
        addressList = [x for x in addressList if type(x) not in (str, unicode)]
        return [EmailAddress(x) for x in addressList]


class Message(MessageBase):
    '''Zimbra Message (an email).'''
    implements(IMessage)

    def __init__(self, zimbra_message):
        MessageBase.__init__(self, zimbra_message)
        self.size = _safe_get_attr(zimbra_message, 's')
        self.conversation_id = _safe_get_attr(zimbra_message, 'cid')
        self.original_id = _safe_get_attr(zimbra_message, '_orig_id')
        self.content = _safe_get_node(zimbra_message, 'content')
        self.message_id_header = _safe_get_node(zimbra_message, 'mid')
        self.sort_field = _safe_get_attr(zimbra_message, 'sf')
        mime = _safe_get_node(zimbra_message, 'mp', None)

        if mime:
            mime = MIMEPart(mime)

        self.mime = mime

    def default_content(self):
        try:
            return self.mime.parts[0].content
        except:
            return ''


class Conversation(MessageBase):
    '''Zimbra Conversation (a mail thread).'''
    def __init__(self, zimbra_conversation):
        MessageBase.__init__(self, zimbra_conversation)
        self.original_id = _safe_get_attr(zimbra_conversation, '_orig_id')
        self.tags = _safe_get_attr(zimbra_conversation, 't')
        self.num_messages = int(_safe_get_attr(zimbra_conversation, 'n', 0))
        self.total = _safe_get_attr(zimbra_conversation, 'total')
        self.mbx = _safe_get_attr(zimbra_conversation, 'mbx')
        self.sort_field = _safe_get_attr(zimbra_conversation, 'sf')
        messages = _safe_get_node(zimbra_conversation, 'm', [])

        if type(messages) != list:
            messages = [messages]

        self.messages = [Message(x) for x in messages]

    def default_content(self):
        try:
            return self.messages[0].default_content()
        except:
            return ''


class Folder:
    '''Zimbra Folder'''
    def __init__(self, zimbra_folder):
        self.raw = zimbra_folder
        self.id = _safe_get_attr(zimbra_folder, 'id')
        self.uuid = _safe_get_attr(zimbra_folder, 'uuid')
        self.name = _safe_get_attr(zimbra_folder, 'name')
        self.parent_id = _safe_get_attr(zimbra_folder, 'l')
        self.parent_uuid = _safe_get_attr(zimbra_folder, 'luuid')
        self.absFolderPath = _safe_get_attr(zimbra_folder, 'absFolderPath')
        self.flags = _safe_get_attr(zimbra_folder, 'f')
        self.unread = int(_safe_get_attr(zimbra_folder, 'u', 0))
        self.type = _safe_get_attr(zimbra_folder, 'view')
        subs = _safe_get_node(zimbra_folder, 'folder', [])
        if not isinstance(subs, list):
            subs = [subs]
        folders = [Folder(x) for x in subs if _safe_get_attr(x, 'name')]
        self.folders = folders


def _date_from_zimbra_date(zimbra_date):
    if not zimbra_date:
        date = None
    else:
        date = DateTime(int(zimbra_date) / 1000)
    return date


def _safe_get_attr(zimbra, key, default=u''):
    if isinstance(zimbra, basestring):
        return default
    return _safe(_get_attr(zimbra, key, default))


def _safe_get_node(zimbra, key, default=u''):
    if isinstance(zimbra, basestring):
        return default
    return _safe(_get_node(zimbra, key, default))


def _get_attr(zimbra, key, default=u''):
    return zimbra._getAttr(key) or default


def _get_node(zimbra, key, default=u''):
    return getattr(zimbra, key, default)


def _safe(val):
    if isinstance(val, basestring):
        val = safe_unicode(val)
    return val
