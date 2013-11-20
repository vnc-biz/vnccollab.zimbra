from zope.annotation.interfaces import IAnnotations

from plone import api


def addZimbraAnnotatedTasks(context, task):
    '''Adds a task to the zimbra annotated tasks of the context.'''
    member = api.user.get_current()
    username = member.getProperty('zimbra_username', '')
    annotatedTasks = getZimbraAnnotatedTasks(context, username)
    annotatedTasks.append(task)
    setZimbraAnnotatedTasks(context, username, annotatedTasks)


def getZimbraAnnotatedTasks(context, username):
    ''' Returns the zimbra tasks annotated associated with the give username
    or [] if anonymous.'''
    if not username:
        return []

    annotation = IAnnotations(context)
    key = _zimbraAnnotatedTaskKey(username)
    annotatedTasks = annotation.get(key, [])
    return annotatedTasks


def _zimbraAnnotatedTaskKey(username):
    '''Returns the key for zimbra tasks annotations associated with a
    username.'''
    return 'vnccollab.zimbra.related_zimbra_task.{0}'.format(username)


def setZimbraAnnotatedTasks(context, username, tasks):
    '''Sets the zimbra tasks annotated associated with the given username.'''
    if not username:
        return

    annotation = IAnnotations(context)
    key = _zimbraAnnotatedTaskKey(username)
    annotation[key] = tasks
