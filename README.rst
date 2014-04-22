vnccollab.zimbra
================

Overview
--------

``vnccollab.zimbra`` offers plone-zimbra integration in the form of
two portlets, one with zimbra calendar and another to access the mail
folders.

Installation
------------

``vnccollab.zimbra`` depends on a fork of ``pyzimbra`` that hasn't
been merged yet upstream, so it's adviseable to use ``mr.developer``
for its installation. Please read INSTALL.rst for more details.

Usage
-----

After installing the package, the User's Personal Information page
is extended with two fields: ``Zimbra Username`` and ``Zimbra Password``.
These fields are needed to authenticate against the zimbra server.

Additionally, there are two new portlets: ``Zimbra: Calendar`` and
``Zimbra: Mail``. These portlets can be added in the usual way.

Known Issues
------------

Due to the use of plone.app.jquery 1.7.2, there could be some issues with
overlays in Plone 4.2.

