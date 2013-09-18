from zope.component import getUtility, getMultiAdapter

from plone import api
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletAssignmentMapping

from vnccollab.zimbra.portlets import zimbra_mail
from vnccollab.zimbra.portlets import zimbra_calendar


MANAGER_NAMES = ['plone.leftcolumn', 'plone.rightcolumn',
                 'plone.dashboard1', 'plone.dashboard2',
                 'plone.dashboard3', 'plone.dashboard4']


def replace_all_portlets():
    '''Replace theme's portlets for zimbra's.'''
    replace_all_general_portlets()
    replace_all_content_portlets()


def replace_all_general_portlets():
    '''Replace portlets for the portal.'''
    portal = api.portal.get()
    managers = get_managers(portal)

    for manager in managers:
        for cat_name, category in manager.items():
            for map_name, mapping in category.items():
                for portlet_name, portlet in mapping.items():
                    new_portlet = new_zimbra_portlet(portlet, portlet_name)
                    if new_portlet is not None:
                        mapping._data[portlet_name] = new_portlet


def replace_all_content_portlets():
    '''Replace portlets in content objects.'''
    all_content = all_content_with_portlets()
    for content in all_content:
        managers = get_managers(content)
        for manager in managers:
            mapping = getMultiAdapter((content, manager), IPortletAssignmentMapping)
            for portlet_name, portlet in mapping.items():
                new_portlet = new_zimbra_portlet(portlet, portlet_name)
                if new_portlet is not None:
                    mapping._data[portlet_name] = new_portlet


def new_zimbra_portlet(portlet, portlet_name):
    '''Given a theme's izmbra portlet and its name, returns a zimbra's one.
    In other case, it returns None.'''
    class_name = _class_name(portlet)
    if class_name == 'vnccollab.theme.portlets.zimbra_mail.Assignment':
        new_portlet = zimbra_mail.Assignment(portlet.header,
                                             portlet.url,
                                             portlet.folder_id,
                                             portlet.count,
                                             portlet.username,
                                             portlet.password,
                                             portlet.timeout,
                                             portlet.request_timeout,
                                             portlet.failure_delay)
        new_portlet.__name__ = portlet_name
        return new_portlet

    elif class_name == 'vnccollab.theme.portlets.zimbra_calendar.Assignment':
        new_portlet = zimbra_calendar.Assignment(portlet.header,
                                                 portlet.url,
                                                 portlet.mail_domain,
                                                 portlet.username,
                                                 portlet.password,
                                                 portlet.calendar_name,
                                                 portlet.timeout,
                                                 portlet.request_timeout,
                                                 portlet.failure_delay)
        new_portlet.__name__ = portlet_name
        return new_portlet

    else:
        return None


def _class_name(obj):
    '''Returns the full qualified class name of an object.'''
    return '{0}.{1}'.format(obj.__module__, obj.__class__.__name__)


def all_content_with_portlets():
    '''Returns all the content objects that have a portlet assigned.'''
    portal = api.portal.get()
    catalog = api.portal.get_tool(name='portal_catalog')

    all_brains = catalog(show_inactive=True, language="ALL",
                         object_provides=ILocalPortletAssignable.__identifier__)
    all_content = [brain.getObject() for brain in all_brains]
    all_content = list(all_content) + [portal]
    return all_content


def get_managers(content):
    '''Returns the portlet managers.'''
    managers = [getUtility(IPortletManager, name=manager_name, context=content)
                    for manager_name in MANAGER_NAMES]
    return managers


def mapping_from_manager(manager, content):
    '''Returns the mappings associated to a portelt manager.'''
    mapping = getMultiAdapter((content, manager), IPortletAssignmentMapping)
    items = mapping.items()
    return items
