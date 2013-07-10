// TODO: error handling
//  * server down, timeout, error
//  * server json 'error' in response

// TODO: move inprogress to on per Pane bases, so that every pane has it's
//       own 'progress' state

// TODO: use separate scrolling for every pane

// TODO: avoid ids, only html classes even for unique identifiers

function zimbra_goBackToEmails(event, eid) {
  // show emails screen
  var target = jq(event.target);
  var portlet = target.parents('.portletZimbraMail').parent();
  var container = target.parents('.portletBody');
  var pane = jq('.emailsView', container);

  // display conversation screen
  container.removeClass('email').addClass('emails');

  return false;
}

function zimbra_goBackToFolders(event) {
  // shows folders listing
  alert('Not implemented yet.');
  return false;
}

function zimbra_newEmail(event) {
  // opens up new email form
  alert('Not implemented yet.');
  return false;
}

function zimbra_clickEmail(event, eid) {
  // dislplays conversation screen
  var target = jq(event.target);
  var portlet = target.parents('.portletZimbraMail').parent();
  var container = target.parents('.portletBody');
  var pane = jq('.emailView', container);

  // set conversation Subject on email pane
  jq('.emailSubject', pane).html(jq('#email_'+eid+'.emailItem .emailSubject',
    container).html());


  // display conversation screen with loader
  container.removeClass('emails').addClass('inprogress email');

  function success(data, textStatus, jqXHR) {
    // update main emails listing
    jq('.emailThread', pane).html(data['conversation']);
    // select item, remove unread class
    jq(jq('.emailItem', container)).removeClass('selected');
    jq(jq('#email_'+eid+'.emailItem', container)).addClass('selected')
      .removeClass('unread');
    // remove progress state
    container.removeClass('inprogress');
  }

  // call server for conversation data
  container.addClass('inprogress');
  jq.post(portal_url + '/@@zimbra-mail-portlet-view',
    {'action': 'email',
     'eid': eid,
     'portlethash': portlet.attr('id').slice('portletwrapper-'.length)},
    success, "json");

  return false;
}

function zimbra_refreshEmails(event, folder) {
  // loads conversations listing into emails screen
  var target = jq(event.target);
  var portlet = target.parents('.portletZimbraMail').parent();
  var container = target.parents('.portletBody');
  var pane = jq('.emailsView', container);

  function success(data, textStatus, jqXHR) {
    // update main emails listing
    pane.html(data['emails']);
    // select first email
    jq(jq('.emailItem', container)).removeClass('selected');
    jq(jq('.emailItem', container)[0]).addClass('selected');
    // update folder label unread messages counter
    jq('.navBarEmails .label .count', container).html(
      jq('.emailItem.unread', container).length);
    // remove progress state
    container.removeClass('inprogress');
  }

  // load folder emails from the server
  container.addClass('inprogress');
  jq.post(portal_url + '/@@zimbra-mail-portlet-view',
    {'action': 'emails',
     'folder': folder,
     'portlethash': portlet.attr('id').slice('portletwrapper-'.length)},
    success, "json");

}

jq(function(event) {
// load inbox emails on page load
jq('.portletZimbraMail .refreshButton').each(function(idx, button) {
  zimbra_refreshEmails({'target': button}, 'inbox');
});

});
