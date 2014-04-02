from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2
from zope.configuration import xmlconfig


class VnccollabZimbraLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    dependencies = [
        'collective.js.jqueryui',
        'collective.customizablePersonalizeForm',
        'vnccollab.common',
        'vnccollab.zimbra',
    ]

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        for package in self.dependencies:
            module = __import__(package, fromlist=[''])
            self.loadZCML(package=module)

        import collective.customizablePersonalizeForm
        xmlconfig.includeOverrides(configurationContext,
                'overrides.zcml',
                package=collective.customizablePersonalizeForm)

        for package in self.dependencies:
            z2.installProduct(app, package)


    def setUpPloneSite(self, portal):
        for package in self.dependencies:
            self.applyProfile(portal, package + ':default')

VNCCOLLAB_ZIMBRA_FIXTURE = VnccollabZimbraLayer()
VNCCOLLAB_ZIMBRA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(VNCCOLLAB_ZIMBRA_FIXTURE,),
    name="VnccollabZimbraLayer:Integration"
)
VNCCOLLAB_ZIMBRA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(VNCCOLLAB_ZIMBRA_FIXTURE, z2.ZSERVER_FIXTURE),
    name="VnccollabZimbraLayer:Functional"
)
