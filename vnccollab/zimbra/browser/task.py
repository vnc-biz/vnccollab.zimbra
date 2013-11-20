from zope import schema
from zope.interface import implements, Interface, Invalid, invariant
from zope.component import getMultiAdapter, getUtility

from z3c.form import form, field, button
from z3c.form.interfaces import IErrorViewSnippet
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from collective.z3cform.datepicker.widget import DatePickerFieldWidget

from vnccollab.zimbra import messageFactory as _
from vnccollab.zimbra.util import IZimbraUtil
from vnccollab.zimbra import annotations


class BothDatesError(Invalid):
    __doc__ == _(u'''Either both or none dates must be provided''')


class IZimbraTaskForm(Interface):
    # TODO: List Id

    # we end it with _ to avoid conflicts in newtask.py
    subject_ = schema.TextLine(
        title=_(u'Subject'),
        description=u'',
        required=True)

    location = schema.TextLine(
        title=_(u'Location'),
        description=_('Task Location'),
        required=False)

    status = schema.Choice(
        title=_(u"Status"),
        description=u'',
        vocabulary='vnccollab.zimbra.vocabularies.StatusZimbraTaskVocabulary',
        required=True)

    # we end it with _ to avoid conflicts in newtask.py
    priority_ = schema.Choice(
        title=_(u"Priority"),
        description=u'',
        vocabulary='vnccollab.zimbra.vocabularies.PrioritiesZimbraTaskVocabulary',
        default='5',
        required=True)

    percentComplete = schema.Choice(
        title=_(u"Percentage of Completion"),
        description=u'',
        vocabulary='vnccollab.zimbra.vocabularies.PercentageZimbraTaskVocabulary',
        required=True)

    startDate = schema.Date(
        title=_(u"Start date"),
        description=u'',
        required=False)

    endDate = schema.Date(
        title=_(u"Due date"),
        description=u'',
        required=False)

    content = schema.Text(
        title=_(u"Description"),
        description=u'',
        required=False,
        default=u'')

    @invariant
    def validateBothDates(data):
        if not data.startDate and not data.endDate:
            return
        if not data.startDate or not data.endDate:
            raise BothDatesError(_(u"You must set both start and end "
                                   u"date or none."))


class ZimbraTaskForm(form.Form):
    implements(IZimbraTaskForm)
    fields = field.Fields(IZimbraTaskForm)

    fields['startDate'].widgetFactory = DatePickerFieldWidget
    fields['endDate'].widgetFactory = DatePickerFieldWidget

    label = _("New Zimbra Task")
    prefix = 'zimbra_task_form'

    formErrorsMessage = _(u"There were some errors.")
    successMessage = _(u"Task was created successfully.")

    ignoreContext = True

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.context.absolute_url() + '/@@' + self.__name__

    @button.buttonAndHandler(_(u"Create"), name='create')
    def handleCreate(self, action):
        """Create zimbra task using SOAP API."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        zimbraUtil = getUtility(IZimbraUtil)
        if not zimbraUtil.authenticate():
            return self.error(u"Authentication Error. Problem in the "
                              u"login/password or Zimbra URL.")

        created = False
        try:
            email = zimbraUtil.get_email_address()
            url = self.context.absolute_url()
            description = self.context.Description()
            content = u'%s\n\n%s' % (url, description)

            data['author'] = email
            data['subject'] = data['subject_']
            data['priority'] = data['priority_']
            data['content'] = content
            task = zimbraUtil.create_task(data)
            annotations.addZimbraAnnotatedTasks(self.context, task)
            created = True

        except Exception:
            plone_utils = getToolByName(self.context, 'plone_utils')
            exception = plone_utils.exceptionString()
            return self.error(u"Unable create issue: " + str(exception))

        else:
            if not created:
                return self.error(u"Task wasn't created, please, check your "
                                  u"settings or contact site administrator "
                                  u"if you are sure your settings are set "
                                  u"properly.")

        self.status = self.successMessage
        IStatusMessage(self.request).addStatusMessage(self.successMessage,
                                                      type='info')
        came_from = self.request.get('HTTP_REFERER') \
            or self.context.absolute_url()
        return self.request.response.redirect(came_from)

    def error(self, msg):
        self.status = msg
        error = getMultiAdapter((Invalid(u''), self.request, None,
                                 None, self, self.context), IErrorViewSnippet)
        error.update()
        self.widgets.errors += (error,)
