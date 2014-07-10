"""
A web2py plugin for creating and displaying ajax-driven html slide shows.

Written by Ian W. Scott (monotasker)

This module file contains most of the business logic.

"""

from plugin_ajaxselect import AjaxSelect
from plugin_widgets import JQMODAL
if 0:
    from gluon import current, URL, Field, IS_IN_DB
    response, db = current.response, current.db
import datetime

#js file necessary for AjaxSelect widget
response.files.insert(5, URL('static',
                          'plugin_ajaxselect/plugin_ajaxselect.js'))
#response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.css'))
response.files.append(URL('static', 'css/plugin_slider.css'))

# db table definitions

db.define_table('plugin_slider_themes',
                Field('theme_name', 'string'),
                Field('description', 'text'),
                Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=request.now),
                format='%(theme_name)s'
                )

db.define_table('plugin_slider_slides',
                Field('slide_name', 'string'),
                Field('slide_content', 'text'),
                Field('theme', 'list:reference plugin_slider_themes'),
                Field('updated', 'datetime', default=datetime.datetime.utcnow()
                      ),
                Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=request.now),
                format='%(slide_name)s'
                )
db.plugin_slider_slides.theme.requires = IS_IN_DB(db,
                                    'plugin_slider_themes.id',
                                    db.plugin_slider_themes._format,
                                    multiple=True)
db.plugin_slider_slides.slide_content.widget = lambda field, value: \
                                        JQMODAL(field, value).textarea('image',
                                                        'image_picker',
                                                        'plugin_widgets',
                                                        'image_picker.load')

db.define_table('plugin_slider_decks',
                Field('deck_name', 'string'),
                Field('deck_slides', 'list:reference plugin_slider_slides'),
                Field('theme', 'list:reference plugin_slider_themes'),
                Field('deck_position', 'integer'),
                Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=request.now),
                format='%(deck_name)s'
                )
db.plugin_slider_decks.deck_slides.requires = IS_IN_DB(db,
                                    'plugin_slider_slides.id',
                                    db.plugin_slider_slides._format,
                                    multiple=True)
db.plugin_slider_decks.theme.requires = IS_IN_DB(db,
                                    'plugin_slider_themes.id',
                                    db.plugin_slider_themes._format,
                                    multiple=True)
db.plugin_slider_decks.deck_slides.widget = lambda field, value: \
                                    AjaxSelect(field, value,
                                               refresher=True,
                                               multi='basic',
                                               lister='simple',
                                               orderby='slide_name',
                                               sortable='true'
                                               ).widget()


class Plugin_slider_decksVirtualFields(object):
    def updated(self):
        deckslides = db(db.plugin_slider_slides.id.belongs(
                        self.plugin_slider_decks.deck_slides)).select()
        datelist = [s.updated for s in deckslides if s.updated is not None]
        if datelist:
            return max(datelist)

db.plugin_slider_decks.virtualfields.append(Plugin_slider_decksVirtualFields())
