from setuptools import setup, find_packages
import os

version = open('version.txt').read()

setup(
    name='vnccollab.zimbra',
    version=version,
    description="VNC Collaboration Zimbra AddOn.",
    long_description=open("README.txt").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Jose Dinuncio',
    author_email='jose.dinuncio@vnc.biz',
    url='http://svn.plone.org/svn/collective/',
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
        'BeautifulSoup',
        'collective.customizablePersonalizeForm',
        'collective.z3cform.datepicker',
        'vnccollab.common',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
