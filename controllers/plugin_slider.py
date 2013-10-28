from pprint import pprint
if 0:
    from gluon import current, UL, LI, DIV, A, URL, MARKMIN, SPAN, SQLFORM
    request, session, db = current.request, current.session, current.db
    response = current.response


def start_deck():
    """
    Initiate showing a plugin_slider slideshow.

    Initialize (create or reset to default) the following session variables
    to control slideshow display:
        plugin_slider_did (int): The id of the current deck
            (from db.plugin_slider)
        plugin_slider_deckorder (list of ints): a list holding the ids of all
            slides in the current deck in their default display order
            of the user's viewing history. This is to allow "back"
            functionality within the deck, particularly if the user jumps
            between slides in a non-default order.

    Send data to view start_deck.load to build the slideshow frame. Then
    call show_slide() to display the first slide of the deck.

    Takes no parameters.
    Expects the first url argument to be the id of the deck to be initialized.
    """
    debug = True

    did = request.args[0]
    if did:
        session['plugin_slider_did'] = did
    else:
        response.flash = "Sorry, I couldn't find the slides you asked for."

    deck = db.plugin_slider_decks[did]
    deckorder = [s for s in deck.deck_slides if s is not None]
    if debug: print deckorder

    if deckorder and len(deckorder) > 0:
        session['plugin_slider_deckorder'] = deckorder
    else:
        response.flash = "Sorry, I couldn't find any slides for that deck."

    firstslide = deckorder[0]
    slidelist = UL(_class='plugin_slider_decklist')
    for d in deckorder:
        theslide = db.plugin_slider_slides[d]
        badges = db((db.tags.slides.contains(theslide.id)) &
                    (db.badges.tag == db.tags.id)).select()
        slidelist.append(LI(A(theslide.slide_name,
                            _href=URL('plugin_slider',
                                      'show_slide',
                                      args=[theslide.id]),
                            cid='plugin_slider_slide')))
        for b in badges:
            if debug: print b.badges.badge_name
            slidelist[-1].append(SPAN(b.badges.badge_name))
    slidemenu = DIV(slidelist, _class='plugin_slider_slidemenu initial_state')

    if debug: print deck.theme
    theme = db.plugin_slider_themes[deck.theme[0]].theme_name

    return dict(did=did, firstslide=firstslide, theme=theme,
                slidemenu=slidemenu, deckorder=deckorder)


def show_slide():
    """
    Assemble and return content of a single slide.

    Takes only one parameter, 'slidearg', an int containing the id of the
    slide to be displayed. This defaults to None. If it is not present
    the function looks for the first URL argument to provide the slide id.

    Returns a dictionary with a single item, 'content', containing a
    web2py MARKMIN helper object with the text contents of the slide.
    """
    try:
        sid = request.args[0]
        session.plugin_slider_sid = sid
    except IndexError:
        try:
            sid = session.plugin_slider_sid
        except Exception:
            print Exception
    except Exception:
        print Exception
        return dict(content='Sorry, no slide was requested.')

    slide = db.plugin_slider_slides[int(sid)]
    print 'sid:', sid
    print 'slide:', slide
    images = db(db.images.id > 0).select().as_list()
    audios = db(db.audio.id > 0).select().as_list()
    # custom markmin tags
    custom_mm = dict(img=lambda text: '<img class="center" src="{}" />'.format(URL('static/images', [i for i in images
                                       if i['title'] == text][0]['image'])),
                     img_r=lambda text: '<img class="pull-right" src="{}" />'.format(URL('static/images', [i for i in images
                                       if i['title'] == text][0]['image'])),
                     img_l=lambda text: '<img src="{}" class="pull-left" />'.format(URL('static/images', [i for i in images
                                       if i['title'] == text][0]['image'])),
                     audio=lambda text: [i for i in audios
                                         if i['title'] == text][0]['audio'])
    content = MARKMIN(slide.slide_content, extra=custom_mm)

    return dict(content=content,
                editform=editform())


def editform():
    """
    Return a sqlform object for editing the specified slide.
    """
    sid = session.plugin_slider_sid
    form = SQLFORM(db.plugin_slider_slides, sid,
                   separator='',
                   deletable=True,
                   showid=True)

    if form.process(formname='plugin_slider_slides/{}'.format(sid)).accepted:
        #the_url = URL('plugin_slider', 'show_slide.load')
        #response.js = "window.setTimeout(" \
                      #"web2py_component('{}', " \
                      #"'plugin_slider_slide'), 500);".format(the_url)
        response.flash = 'The changes were recorded successfully.'
        print '\n\nform processed'
    elif form.errors:
        print '\n\nlistandedit form errors:'
        pprint({k: v for k, v in form.errors.iteritems()})
        print '\n\nlistandedit form vars'
        pprint({k: v for k, v in form.vars.iteritems()})
        print '\n\nlistandedit request vars'
        pprint({k: v for k, v in request.vars.iteritems()})
        response.flash = 'Sorry, there was an error processing ' \
                         'the form. The changes have not been recorded.'

    else:
        print '\n\nform not processed, but no errors'
        pprint({k: v for k, v in form.vars.iteritems()})
        pprint({k: v for k, v in request.vars.iteritems()})
        pass

    return form


def next_slide():
    """
    Find the next slide in a deck sequence and redirect to
    show_slide to display its content. If already at the last slide,
    simply present it again and give the user a response.flash message.
    """

    sid = session.plugin_slider_sid
    deckorder = session.plugin_slider_deckorder
    curr_i = deckorder.index(int(sid))
    new_i = curr_i + 1
    if len(deckorder) > new_i:
        session.plugin_slider_sid = deckorder[new_i]
    else:
        response.flash = 'You are already at the last slide.'
    return show_slide()


def prev_slide():
    """
    Find the previous slide in a deck sequence and redirect to
    show_slide to display its content. If already at the first slide,
    simply present it again and give the user a response.flash message.
    """

    sid = session.plugin_slider_sid
    deckorder = session.plugin_slider_deckorder
    curr_i = deckorder.index(int(sid))
    new_i = curr_i - 1
    if new_i >= 0:
        session.plugin_slider_sid = deckorder[new_i]
    else:
        response.flash = 'You are already at the last slide.'
    return show_slide()
