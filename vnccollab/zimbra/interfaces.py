from zope.interface import Interface, Attribute


class IAddOnInstalled(Interface):
        '''Layer specific intrface for this add-on.'''


class IEmailAddress(Interface):
    '''Represents a Zimbra Email address.'''

    type = Attribute('The type of mail (from/to/cc/bcc/...)')
    email_address = Attribute('The user@domain part of an address')
    personal_name = Attribute('The comment/name part of an address')
    display_name = Attribute('First name or login of an address')
    content_name = Attribute('The original email string')


class IMessage(Interface):
    '''Represents a Zimbra message (email).'''

    id = Attribute('Message id')
    flags = Attribute('Message flags')
    size = Attribute('Message Size')
    date = Attribute('Date in the header of the message')
    conversation_id = Attribute('Id of the conversation')
    original_id = Attribute('Id of the original message on the thread')
    subject = Attribute('Subject of the message')
    fragment = Attribute('First bytes of the message')
    addresses = Attribute('Addresses in the message')
    content = Attribute('The raw content of the message')
    multipart = Attribute('Root of the multipart Representation')
    message_id_header = Attribute('Message id header')
    raw = Attribute('The raw zimbra message structure')

    def filter_addresses(filter):
        '''Returns only a particular type of email from addresses.'''

# Utilities


class IZimbraUtil(Interface):
    """Interface for Zimbra Utility"""

    def authenticate():
        ''' '''

    def get_email_address():
        ''' '''

    def search(query):
        ''' '''

    def get_raw_emails(**query):
        ''' '''

    def get_messages(**query):
        ''' '''

    def get_message(eid):
        ''' '''

    def get_conversations(**query):
        ''' '''

    def get_conversation(eid):
        ''' '''

    def get_email_thread(eid):
        ''' '''

    def get_address_book(offset=0, limit=100):
        ''' '''

    def get_tasks():
        ''' '''

    def create_task(dct):
        ''' '''
