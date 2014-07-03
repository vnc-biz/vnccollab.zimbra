from setuptools import setup, find_packages
import os

version = open('version.txt').readline().strip()

setup(
    name='vnccollab.zimbra',
    version=version,
    description="VNC Collaboration Zimbra AddOn.",
    long_description=open("README.rst").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.rst")).read(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    keywords='zimbra mail',
    author='Jose Dinuncio',
    author_email='jose.dinuncio@vnc.biz',
    url='https://github.com/vnc-biz/vnccollab.zimbra',
    license='gpl',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['vnccollab'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pyzimbra',
        'five.grok',
        'plone.api',
        'requests',
        'BeautifulSoup',
        'simplejson',
        'wsapi4plone.core',
        'plone.app.jquery>=1.7.2',
        'plone.app.jquerytools>=1.4',
        'collective.customizablePersonalizeForm',
        'collective.z3cform.datepicker',
        'vnccollab.common',
    ],
    extras_require={'test': ['plone.app.testing']},
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
