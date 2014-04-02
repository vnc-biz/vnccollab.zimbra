import unittest2 as unittest

from DateTime import DateTime

from vnccollab.zimbra.content import EmailAddress, MIMEPart
from vnccollab.zimbra.content import Message, Conversation, Folder

from vnccollab.zimbra.tests.mock_zimbra import MockZimbra
from vnccollab.zimbra.testing import VNCCOLLAB_ZIMBRA_FIXTURE


class BasicMockupTestCase(unittest.TestCase):
    """Base Class for content tests."""

    layer = VNCCOLLAB_ZIMBRA_FIXTURE


class EmailAddressTest(BasicMockupTestCase):

    def setUp(self):
        mail_attrs = dict(
            t='f',
            a='me@blah.com',
            p='me',
            d='Sir. Me'
        )
        mail_nodes = dict(
            e='some content'
        )
        mail_mock = MockZimbra(attrs=mail_attrs, nodes=mail_nodes)
        self.mail = EmailAddress(mail_mock)

    def test_type(self):
        self.assertEquals(self.mail.type, self.mail.FROM)

    def test_email_address(self):
        self.assertEquals(self.mail.email_address, 'me@blah.com')

    def test_personal_name(self):
        self.assertEquals(self.mail.personal_name, 'me')

    def test_display_name(self):
        self.assertEquals(self.mail.display_name, 'Sir. Me')

    def test_content_name(self):
        self.assertEquals(self.mail.content_name, u'some content')


class MIMEPartTest(BasicMockupTestCase):

    def setUp(self):
        mime_attrs = dict(
            part='first',
            body='1',
            s=1024,
            mid=123,
            cid=124,
            truncated='0',
            ct='text/plain',
            filename='fname',
            ci='abcdef',
            cl='',
            cd=''
        )
        mime_nodes = dict(
            content='hello world',
            mp=[]
        )
        self.mime_raw = MockZimbra(nodes=mime_nodes, attrs=mime_attrs)
        self.mime = MIMEPart(self.mime_raw)

    def test_raw(self):
        self.assertEquals(self.mime.raw, self.mime_raw)

    def test_part_name(self):
        self.assertEquals(self.mime.part_name, 'first')

    def test_is_body(self):
        self.assertTrue(self.mime.is_body)

    def test_size(self):
        self.assertEquals(self.mime.size, 1024)

    def test_message_id(self):
        self.assertEquals(self.mime.message_id, 123)

    def test_conversation_id(self):
        self.assertEquals(self.mime.conversation_id, 124)

    def test_content_type(self):
        self.assertEquals(self.mime.content_type, 'text/plain')

    def test_content(self):
        self.assertEquals(self.mime.content, 'hello world')

    def test_parts(self):
        self.assertEquals(self.mime.parts, [])


class MessageAndConversationTest(BasicMockupTestCase):

    def setUp(self):
        mail_attrs = dict(
            t='f',
            a='me@blah.com',
            p='me',
            d='Sir. Me'
        )
        mail_nodes = dict(
            e='some content'
        )
        self.mail_raw = MockZimbra(attrs=mail_attrs, nodes=mail_nodes)

        msg_attrs = dict(
            id='1234',
            f='ab',
            d='1395311245000',
            s=1024,
            cid='234',
            _orig_id='233',
            sf='subject',
        )
        msg_nodes = dict(
            su='this is a message',
            fr='this is a fragment',
            e=[self.mail_raw],
            content='this is the body',
            mid='these are headers',
            mp=[],
        )
        self.msg_raw = MockZimbra(attrs=msg_attrs, nodes=msg_nodes)
        self.msg = Message(self.msg_raw)

        conv_attrs = dict(
            id='234',
            f='',
            d='1395311246000',
            _orig_id='211',
            t='tags',
            n=1,
            total=1,
            mbx='mbx',
            sf='title',
        )
        conv_nodes = dict(
            su='this is a conversation',
            fr='conversation fragment',
            e=[self.mail_raw],
            m=[self.msg_raw],

        )
        self.conv_raw = MockZimbra(attrs=conv_attrs, nodes=conv_nodes)
        self.conv = Conversation(self.conv_raw)

    def test_msg_raw(self):
        self.assertEquals(self.msg.raw, self.msg_raw)

    def test_msg_id(self):
        self.assertEquals(self.msg.id, '1234')

    def test_msg_flags(self):
        self.assertEquals(self.msg.flags, 'ab')

    def test_msg_date(self):
        self.assertEquals(self.msg.date, DateTime(1395311245))

    def test_msg_subject(self):
        self.assertEquals(self.msg.subject, 'this is a message')

    def test_msg_fragment(self):
        self.assertEquals(self.msg.fragment, 'this is a fragment')

    def test_msg_addresses(self):
        self.assertEquals(len(self.msg.addresses), 1)

    def test_msg_size(self):
        self.assertEquals(self.msg.size, 1024)

    def test_msg_conversation_id(self):
        self.assertEquals(self.msg.conversation_id, '234')

    def test_msg_original_id(self):
        self.assertEquals(self.msg.original_id, '233')

    def test_msg_content(self):
        self.assertEquals(self.msg.content, 'this is the body')

    def test_msg_message_id_header(self):
        self.assertEquals(self.msg.message_id_header, 'these are headers')

    def test_msg_sort_field(self):
        self.assertEquals(self.msg.sort_field, 'subject')

    def test_msg_mime(self):
        self.assertEquals(self.msg.mime, [])

    #  Conversation

    def test_conv_raw(self):
        self.assertEquals(self.conv.raw, self.conv_raw)

    def test_conv_original_id(self):
        self.assertEquals(self.conv.original_id, '211')

    def test_conv_id(self):
        self.assertEquals(self.conv.id, '234')

    def test_conv_messages(self):
        messages = self.conv.messages
        self.assertEquals(len(messages), 1)
        msg = messages[0]
        self.assertEquals(msg.id, self.msg.id)


class FolderTest(BasicMockupTestCase):

    def setUp(self):
        folder_attrs = dict(
            id='123',
            uuid='abc',
            name='inbox',
            l='12',
            luuid='def',
            absFolderPath='/inbox',
            f='',
            u=0,
            view='f',
        )
        folder_nodes = dict(
            folder=[],
        )
        self.folder_raw = MockZimbra(attrs=folder_attrs, nodes=folder_nodes)
        self.folder = Folder(self.folder_raw)

    def test_raw(self):
        self.assertEquals(self.folder.raw, self.folder_raw)

    def test_id(self):
        self.assertEquals(self.folder.id, '123')

    def test_uuid(self):
        self.assertEquals(self.folder.uuid, 'abc')

    def test_name(self):
        self.assertEquals(self.folder.name, 'inbox')

    def test_parent_id(self):
        self.assertEquals(self.folder.parent_id, '12')

    def test_parent_uuid(self):
        self.assertEquals(self.folder.parent_uuid, 'def')

    def test_absFolderPath(self):
        self.assertEquals(self.folder.absFolderPath, '/inbox')

    def test_flags(self):
        self.assertEquals(self.folder.flags, '')

    def test_unread(self):
        self.assertEquals(self.folder.unread, 0)

    def test_subs(self):
        self.assertEquals(self.folder.folders, [])
