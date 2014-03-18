.. contents::

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
for its installation. Please read INSTALL.txt for more details.

Usage
-----

After installing the package, the User's Personal Information page
is extended with two fields: ``Zimbra Username`` and ``ZImbra Password``.
These fields are needed to authenticate against the zimbra server.

Additionally, there are two new portlets: ``Zimbra: Calendar`` and
``Zimbra: Mail``. These portlets can be added n the usual way.