vnccollab.zimbra Installation
-----------------------------

The preferred way to install ``vnccollab.zimbra`` is using buildout.
``vnccollab.zimbra`` depends on a fork of ``pyzimbra`` that hasn't
been merged yet upstream, so it's adviseable to use ``mr.developer``.

A zc.buildout and the plone.recipe.zope2instance
recipe to manage your project, you can do this:

* Add ``vnccollab.zimbra`` to the list of eggs to install, e.g.: ::

    [buildout]
    ...
    extensions +=
        mr.developer

    eggs =
        ...
        pyzimbra
        vnccollab.zimbra

    auto-checkout =
      pyzimbra

    [sources]
    # we are currently using our fork of pyzimbra
    pyzimbra = git git://github.com/vnc-biz/pyzimbra.git branch=master

* Tell the plone.recipe.zope2instance recipe to install a ZCML slug: ::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        ${buildout:eggs}
        ...
        vnccollab.zimbra-overrides

* Set vnccollab.zimbra dependency versions: ::

    [versions]
    collective.js.jqueryui = 1.8.16.8
    plone.app.jquery = 1.7.2
    plone.app.jquerytools = 1.4

* Re-run buildout, e.g. with: ::

    $ ./bin/buildout

You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.

