import json
import base64
import os.path

from AccessControl import getSecurityManager
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFCore import permissions
from plone.memoize.instance import memoize

from wsapi4plone.core.browser.app import ApplicationAPI

'''
This module contains the views to allow Zimbra to interact with plone.

All these views are server as XMLRPC methods. They return a string with the
result encoded as JSON.
'''


class LiveSearchReplyJson(BrowserView):
    OMIT_TYPES = ['Folder']

    def search_string(self, string):
        '''Returns the objects that satisfy the query indicated by the
        string.'''
        plone_utils = getToolByName(self.context, 'plone_utils')
        friendly_types = plone_utils.getUserFriendlyTypes()
        keys = ' AND '.join(string.split())
        dct = {'SearchableText': keys,
               'portal_type': friendly_types, }
        return self.search_dict(dct)

    def search_dict(self, dct):
        '''Returns the objects that satisfy the query indicated by the
        dictionary.'''
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(**dct)
        return results

    def _get_lost_icon(self, brain):
        '''Gets the icon of a brain if it is not present'''
        return '{0}{1}'.format(self.context.portal_url(),
                               '/++resource++vnccollab.zimbra.images/doc.png')

    def _tuples_from_brains(self, brains):
        '''Converts a list of brains to a list of tuples'''
        plone_view = self.context.restrictedTraverse('@@plone')
        plone_utils = getToolByName(self.context, 'plone_utils')
        pretty_title_or_id = plone_utils.pretty_title_or_id

        tuples = []

        for brain in brains:
            type_ = brain.portal_type

            if type_ not in self.OMIT_TYPES:
                title = pretty_title_or_id(brain)
                url = brain.getURL()
                icon = plone_view.getIcon(brain).url or self._get_lost_icon(brain)
                description = brain.Description
                subject = brain.Subject
                creator = brain.Creator
                creationDate = brain.CreationDate
                modificationDate = brain.ModificationDate

                tuples.append((icon, type_, title, url, description,
                               subject,
                               creator, creationDate, modificationDate))

        return tuples

    def _sanitize_query_string(self, query):
        '''Cleans the query string'''
        multispace = u'\u3000'.encode('utf-8')
        for char in ('?', '-', '+', '*', multispace):
                query = query.replace(char, ' ')
        return query

    def __call__(self, REQUEST, RESPONSE):
        '''Returns a JSON representation of the objects that satisfy the query'''
        if type(REQUEST) == str:
            query = self._sanitize_query_string(REQUEST)
            brains = self.search_string(query)
        elif type(REQUEST) == dict:
            brains = self.search_dict(REQUEST)
        results = self._tuples_from_brains(brains)
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(results)


class GetObjectJson(BrowserView):
    '''Implements get_object_json.

    Returns a string with a JSON representation of the current object.

    The representation is a dictionary with the data obtained by wsapi4plone's
    get_object with dates converted to strings.'''

    def __call__(self, REQUEST, RESPONSE):
        '''Returns a JSON representation of the current object'''
        wsapi = ApplicationAPI(self.context, self.request)
        results = wsapi.get_object()
        # One result is a tuple (object_data, object_type, extra_info)
        # We're interested only in object_data
        result = results.values()[0][0]
        self._sanitize_results(result)
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(result)

    SANITIZE_FIELDS = ['DateTime']

    def _sanitize_results(self, result):
        for k, v in result.items():
            if v.__class__.__name__ in self.SANITIZE_FIELDS:
                result[k] = str(v)

        # Convert file data to string instead of xmlrpclib.Binary
        if 'file' in result:
            result['file']['data'] = base64.b64encode(result['file']['data'].data)


class GetTreeJson(BrowserView):
    '''Returns a string with a JSON representation of the tree of folders
    accesible by the current user.
    '''
    CONTAINER_TYPES = ['Folder']

    def __call__(self, REQUEST, RESPONSE):
        result = self._get_tree()
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(result)

    def _get_tree(self):
        '''Returns a tree structure with the container types allowed.'''
        # TODO: Search only below context
        catalog = getToolByName(self.context, 'portal_catalog')
        params = {'portal_type': self.CONTAINER_TYPES, }
        brains = catalog(**params)

        brains_and_parents = [self._brain_and_parents(x) for x in brains]
        brains_and_parents = [x for sublist in brains_and_parents
                                for x in sublist]
        brains = self._remove_repeated_brains(brains_and_parents)

        results = [self._dict_from_brain(x) for x in brains]
        results = self._sorted(results, reverse=True)
        tree = self._create_tree(results)
        tree = self._prune_tree(tree)
        tree = self._sort_tree(tree)
        return tree

    def _brain_and_parents(self, brain):
        '''Returns a list of a brain and all its parents.'''
        path = os.path.dirname(brain.getPath())
        parent = self._brain_from_path(path)

        if not parent:
            return [brain]
        else:
            return [brain] + self._brain_and_parents(parent)

    def _remove_repeated_brains(self, brains):
        '''Returns a list of unique brains.'''
        paths = []
        new_brains = []
        for brain in brains:
            path = brain.getPath()
            if path not in paths:
                paths.append(path)
                new_brains.append(brain)

        return new_brains

    @memoize
    def _brain_from_path(self, path):
        '''Returns a brain given its path or None'''
        catalog = getToolByName(self.context, 'portal_catalog')
        query = dict(path={"query": path, "depth": 0})
        brains = catalog(**query)

        if len(brains) == 1:
            return brains[0]
        else:
            return None

    def _prune_tree(self, tree):
        '''Prunes a tree from unwanted nodes'''
        new_tree = []
        for item in tree:
            if item['portal_type'] not in self.CONTAINER_TYPES:
                continue
            content = self._prune_tree(item['content'])
            new_item = dict(item)
            new_item['content'] = content
            new_tree.append(new_item)

        return new_tree

    def _sorted(self, lst, reverse=False):
        '''Returns the folders sorted by the lenght of its path'''
        return sorted(lst, lambda x, y: cmp(len(x['path']), len(y['path'])),
                      reverse=reverse)

    def _inside(self, son, father):
        '''True if the folder son is inside father'''
        return os.path.dirname(son['path']) == father['path']

    def _create_tree(self, lst):
        '''Creates the folder tree.'''
        tree = []
        for i, e in enumerate(lst):
            for f in lst[i + 1:]:
                if self._inside(e, f):
                    f['content'].append(e)
                    break
            else:
                tree.append(e)
        return tree

    def _dict_from_brain(self, brain):
        '''Returns a dict representing the folder, given a brain'''
        return {'id': brain.getId,
                'title': brain.Title,
                'path': brain.getPath(),
                'portal_type': brain.portal_type,
                'writable': self._is_container_writable(brain),
                'content': []}

    def _is_container_writable(self, brain):
        '''True if the current user can write in the brain's container.

        NOTE: We need to access to the associate object, and this could
        be time consuming. In case of degradation of speed, check here.
        '''
        obj = brain.getObject()
        perm = getSecurityManager().checkPermission(
                        permissions.AddPortalContent, obj)
        return perm == 1

    def _sort_tree(self, tree):
        tree = sorted(tree, lambda x, y: cmp(x['title'], y['title']))
        for e in tree:
            e['content'] = self._sort_tree(e['content'])
        return tree


class SetFilenameJson(BrowserView):
    '''Sets the filename of a ATFile object.

    This should be done using by wsapi4plone.core, but since it is unable,
    we'll do it here.

    Returns an empty string is everything is OK or an error message.'''

    def __call__(self, REQUEST, RESPONSE):
        '''Returns a JSON representation of the current object'''
        result = ''
        try:
            context = self.context
            default_filename = utils.pretty_title_or_id(context, context) + '.pdf'
            filename = REQUEST.get('filename', default_filename)
            self.context.setFilename(filename)
        except Exception, e:
            result = str(e)
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(result)


class GetListOfSearchParameters(BrowserView):
    '''Get the list of valid tags, item types and review status for a search.'''

    def __call__(self, REQUEST, RESPONSE):
        '''Returns a JSON representation of the current object'''
        result = []
        try:
            if REQUEST == 'Subject':
                result = self._get_subject()
            elif REQUEST == 'portal_type':
                result = self._get_portal_type()
            elif REQUEST == 'review_state':
                result = self._get_review_state()
            else:
                result = []
        except Exception, e:
            result = str(e)
        RESPONSE.setHeader('Content-Type', 'application/json')
        return json.dumps(result)

    def _get_subject(self):
        '''Returns a list of (id, title) of all Tags.'''
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        return [(x, x) for x in portal_catalog.uniqueValuesFor('Subject')]

    def _get_portal_type(self):
        '''Returns a list of (id, title) of all Portal Types.'''
        portal_types = getToolByName(self.context, 'portal_types')
        portal_properties = getToolByName(self.context, 'portal_properties')
        metaTypesNotToList = portal_properties.navtree_properties.metaTypesNotToList
        types = [x for x in portal_types.keys()
                   if x not in metaTypesNotToList]
        return [(x, portal_types[x].title) for x in types]

    def _get_review_state(self):
        '''Returns a list of (id, title) of all Review states.'''
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        workflows = [portal_workflow[x[0]]
                        for x in portal_workflow.workflows_in_use() if x]
        states_list = [wf.states.items() for wf in workflows]
        # state_list is a list of lists of states. Let's make it plain
        states = []
        for st in states_list:
            states.extend(st)
        state_info = [(s[0], s[1].title) for s in states]
        # Some states have different names, we'll use the first one
        states = []
        for st in state_info:
            if st[0] not in [s[0] for s in states]:
                states.append(st)
        return states
