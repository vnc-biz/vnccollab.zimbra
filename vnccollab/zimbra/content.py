from DateTime import DateTime

from zope.interface import implements
from Products.CMFPlone.utils import safe_unicode

from vnccollab.zimbra.interfaces import IEmailAddress, IMessage


class EmailAddress:
    '''Implementation of a Zimbra Email.'''
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


class Message:
    '''Implementation of a Zimbra Message.'''
    implements(IMessage)

    def __init__(self, zimbra_message):
        self.id = _safe_get_attr(zimbra_message, 'id')
        self.flags = _safe_get_attr(zimbra_message, 'f')
        self.size = _safe_get_attr(zimbra_message, 's')
        self.date = _date_from_zimbra_date(_get_attr(zimbra_message, 'd'))
        self.conversation_id = _safe_get_attr(zimbra_message, 'cid')
        self.original_id = _safe_get_attr(zimbra_message, '_orig_id')
        self.subject = _safe_get_node(zimbra_message, 'su')
        self.fragment = _safe_get_node(zimbra_message, 'fr')
        self.addresses = [EmailAddress(x) for x in
                            _safe_get_node(zimbra_message, 'e')]
        self.content = _safe_get_node(zimbra_message, 'content')
        self.multipart = _safe_get_node(zimbra_message, 'mp')
        self.message_id_header = _safe_get_node(zimbra_message, 'mid')
        self.raw = zimbra_message

    def filter_addresses(self, filter):
        return [email for email in self.addresses if email.type == filter]


def _date_from_zimbra_date(zimbra_date):
    if not zimbra_date:
        date = None
    else:
        date = DateTime(int(zimbra_date) / 1000)
    return date


def _safe_get_attr(zimbra, key, default=u''):
    return _safe(_get_attr(zimbra, key, default))


def _safe_get_node(zimbra, key, default=u''):
    return _safe(_get_node(zimbra, key, default))


def _get_attr(zimbra, key, default=u''):
    return zimbra._getAttr(key) or default


def _get_node(zimbra, key, default=u''):
    return getattr(zimbra, key, default)


def _safe(val):
    if isinstance(val, basestring):
        val = safe_unicode(val)
    return val
