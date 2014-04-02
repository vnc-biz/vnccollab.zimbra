from zope.component import getUtility, getMultiAdapter

from Products.GenericSetup.utils import _getDottedName

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager

from vnccollab.zimbra.tests.base import FunctionalTestCase
from vnccollab.zimbra.portlets import zimbra_mail


MAIL_PORTLET = 'vnccollab.zimbra.portlets.ZimbraMailPortlet'
CALENDAR_PORTLET = 'vnccollab.zimbra.portlets.ZimbraCalendarPortlet'


class PortletTest(FunctionalTestCase):
    def setUp(self):
        super(PortletTest, self).setUp()
        self.setRoles(('Manager', ))

    def test_ZimbraMailPortletRegistered(self):
        portlet = getUtility(IPortletType, name=MAIL_PORTLET)
        self.assertEquals(portlet.addview, MAIL_PORTLET)

    def test_ZimbraMailCalendarPortletRegistered(self):
        portlet = getUtility(IPortletType, name=CALENDAR_PORTLET)
        self.assertEquals(portlet.addview, CALENDAR_PORTLET)

    def test_RegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name=MAIL_PORTLET)
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces)

    def test_Interfaces(self):
        portlet = zimbra_mail.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_InvokeAddViewOnMailPortlet(self):
        portlet = getUtility(IPortletType, name=MAIL_PORTLET)
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.rightcolumn')

        for m in mapping.keys():
            del mapping[m]

        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                        zimbra_mail.Assignment))

    def test_InvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.portal.REQUEST

        mapping['foo'] = zimbra_mail.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, zimbra_mail.EditForm))

    def test_Renderer(self):
        context = self.portal
        request = self.portal.REQUEST
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager,
                             name='plone.leftcolumn',
                             context=self.portal)
        assignment = zimbra_mail.Assignment()

        renderer = getMultiAdapter((context, request, view,
                                    manager, assignment),
                                   IPortletRenderer)
        #print renderer.refresh()
        #print renderer.getTickets()
        self.failUnless(isinstance(renderer, zimbra_mail.Renderer))
