#from Products.CMFCore.utils import getToolByName
from plone.app.upgrade.utils import installOrReinstallProduct
from plone import api

from vnccollab.zimbra.config import PROJECTNAME


DEFAULT_PROFILE = 'profile-%s:default' % PROJECTNAME


def upgrade_1001_1002(context):
    '''Installs vnccollab.common.'''
    portal = api.portal.get()
    installOrReinstallProduct(portal, 'vnccollab.common')