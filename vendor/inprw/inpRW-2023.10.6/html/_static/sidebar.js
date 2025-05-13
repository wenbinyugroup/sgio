/*
 * sidebar.js
 * ~~~~~~~~~~
 *
 * This script makes the Sphinx sidebar collapsible. This is a slightly
 * modified version of Sphinx's own sidebar.js.
 *
 * .sphinxsidebar contains .sphinxsidebarwrapper.  This script adds in
 * .sphixsidebar, after .sphinxsidebarwrapper, the #sidebarbutton used to
 * collapse and expand the sidebar.
 *
 * When the sidebar is collapsed the .sphinxsidebarwrapper is hidden and the
 * width of the sidebar and the margin-left of the document are decreased.
 * When the sidebar is expanded the opposite happens.  This script saves a
 * per-browser/per-session cookie used to remember the position of the sidebar
 * among the pages.  Once the browser is closed the cookie is deleted and the
 * position reset to the default (expanded).
 *
 * :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */

$(function() {
  // global elements used by the functions.
  // the 'sidebarbutton' element is defined as global after its
  // creation, in the add_sidebar_button function
  var bodywrapper = $('.bodywrapper');
  var sidebar = $('.sphinxsidebar');
  var sidebarwrapper = $('.sphinxsidebarwrapper');

  // original margin-left of the bodywrapper and width of the sidebar
  // with the sidebar expanded
  var bw_margin_expanded = bodywrapper.css('margin-left');
  var ssb_width_expanded = sidebar.width();

  // margin-left of the bodywrapper and width of the sidebar
  // with the sidebar collapsed
  var bw_margin_collapsed = '1.5em';
  var ssb_width_collapsed = '1.5em';

  // colors used by the current theme
  var dark_color = '#ABABAB';
  var light_color = '#ABABAB';

  function sidebar_is_collapsed() {
    return sidebarwrapper.is(':not(:visible)');
  }

  function toggle_sidebar() {
    if (sidebar_is_collapsed())
      expand_sidebar();
    else
      collapse_sidebar();
  }

  function collapse_sidebar() {
    sidebarwrapper.hide();
    sidebar.css('width', ssb_width_collapsed);
    bodywrapper.css('margin-left', bw_margin_collapsed);
    sidebarbutton.css({
        'margin-left': '0',
        'border-radius': '0',
		'width': 25
    });
    sidebarbutton.find('span').text('»');
    sidebarbutton.attr('title', _('Expand sidebar'));
    document.cookie = 'sidebar=collapsed';
  }

  function expand_sidebar() {
    bodywrapper.css('margin-left', bw_margin_expanded);
    sidebar.css('width', ssb_width_expanded);
    sidebarwrapper.show();
    sidebarbutton.css({
        'margin-left': ssb_width_expanded-25,
        'border-radius': '0',
        'font-size': '2em'
    });
    sidebarbutton.find('span').text('«');
    sidebarbutton.attr('title', _('Collapse sidebar'));
    document.cookie = 'sidebar=expanded';
  }

  function add_sidebar_button() {
    sidebarwrapper.css({
        'float': 'left',
        'margin-right': '0',
        'width': ssb_width_expanded - 25
    });
    // create the button
    sidebar.append(
      '<div id="sidebarbutton"><span>&laquo;</span></div>'
    );
    var sidebarbutton = $('#sidebarbutton');
    sidebarbutton.find('span').css({
        'height': '100%',
		    'margin-left': '4px',
    });

    sidebarbutton.click(toggle_sidebar);
    sidebarbutton.attr('title', _('Collapse sidebar'));
    sidebarbutton.css({
        'border-radius': '0',
        'color': '#FFFFFF',
        'font-size': '2em',
        'cursor': 'pointer',
        'padding-left': '1px',
        'margin-left': ssb_width_expanded-25,
        'width': 25
    });

    sidebarbutton.hover(
      function () {
          $(this).css('background-color', dark_color);
      },
      function () {
          $(this).css('background-color', light_color);
      }
    );
  }

  function set_position_from_cookie() {
    if (!document.cookie)
      return;
    var items = document.cookie.split(';');
    for(var k=0; k<items.length; k++) {
      var key_val = items[k].split('=');
      var key = key_val[0];
      if (key == 'sidebar') {
        var value = key_val[1];
        if ((value == 'collapsed') && (!sidebar_is_collapsed()))
          collapse_sidebar();
        else if ((value == 'expanded') && (sidebar_is_collapsed()))
          expand_sidebar();
      }
    }
  }

  add_sidebar_button();
  var sidebarbutton = $('#sidebarbutton');
  set_position_from_cookie();
});