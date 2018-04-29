import xml.etree.ElementTree as ET
import configparser
import re
from functools import partial
from shutil import copy2
from pathlib import PurePath
from os import path

from appJar import gui

WINDOW_NAME = "ROM filter"
APP_NAME = "ROM filter"


def extract_control_attribute(controls, name):
    extracted_value = None

    for control in controls:
        value = control.get(name)
        if extracted_value is None:
            extracted_value = value
        elif extracted_value != value:
            return 'mixed'

    if extracted_value is None:
        return 'None'  # So that it can be specified at the command line

    return extracted_value


def add_game_to_data(store, key, game_name):
    if key not in store:
        store[key] = []
    store[key].append(game_name)


def filter_games(store, filter_criteria, games):
    if filter_criteria is None or len(filter_criteria) == 0:
        return games

    filtered_games = games

    excluded_criteria = set(store.keys()).difference(set(filter_criteria))
    for criteria in excluded_criteria:
        filtered_games = filtered_games.difference(store[criteria])

    return filtered_games


data_all_games = []
data_clones = []
data_control_types = {}
data_control_buttons = {}
data_driver_emulation = {}
data_categories = {}
data_filtered_games = []


def get_filters(xml):
    tree = ET.parse(xml)
    machines = tree.findall('machine')

    for machine in machines:
        name = machine.get('name')
        if machine.get('runnable') == 'no':
            continue
        print('processing', name, end="\r")

        data_all_games.append(name)

        if machine.get('cloneof') is not None:
            data_clones.append(name)

        game_inputs = machine.findall('input')
        if game_inputs is None or len(game_inputs) == 0:
            print('ERROR:', name, 'did not have an <input> specified')
        elif len(game_inputs) > 1:
            print('ERROR:', name, 'had too many <input> elements specified')
        else:
            game_controls = game_inputs[0].findall('control')
            if game_controls is None or len(game_controls) == 0:
                add_game_to_data(data_control_types, 'None', name)
            else:
                game_type = extract_control_attribute(game_controls, 'type')
                add_game_to_data(data_control_types, game_type, name)

                if game_type in ['joy', 'stick', 'dial', 'only_buttons', 'lightgun', 'trackball', 'doublejoy',
                                 'paddle', 'mouse', 'pedal']:
                    add_game_to_data(data_control_buttons, extract_control_attribute(game_controls, 'buttons'),
                                     name)

        game_driver = machine.findall('driver')
        if game_driver is None or len(game_driver) == 0:
            print('ERROR:', name, 'did not have an <driver> specified')
        elif len(game_driver) > 1:
            print('ERROR:', name, 'had too many <driver> elements specified')
        else:
            add_game_to_data(data_driver_emulation, game_driver[0].get('emulation'), name)

    print('clones')
    print('control-type:')
    print(data_control_types.keys())
    print('buttons:')
    print(data_control_buttons.keys())
    print('emulation:')
    print(data_driver_emulation.keys())


def safe_convert_to_int(number_string):
    try:
        return int(number_string)
    except ValueError:
        return 0


def setup_driver_xml_filters_ui(app):
    get_filters(app.getEntry('xml'))

    with app.frame("driver options", sticky="new"):
        with app.labelFrame("Control Types", row=0, column=0, colspan=2, rowspan=3):
            i = 0
            for key in sorted(data_control_types.keys()):
                app.checkBox(title="control_%s" % key, value=True, name=key, column=i % 3, row=int(i / 3))
                app.setCheckBoxChangeFunction("control_%s" % key, partial(refresh_filtered_games, app))
                i += 1

        with app.labelFrame("Emulation Status", row=0, column=2):
            i = 0
            for key in sorted(data_driver_emulation.keys()):
                app.checkBox(title="emulation_%s" % key, value=True, name=key, column=i % 2, row=int(i / 2))
                app.setCheckBoxChangeFunction("emulation_%s" % key, partial(refresh_filtered_games, app))
                i += 1

        with app.labelFrame("Max Buttons", row=1, column=2, sticky="new"):
            converted_button_numbers = [safe_convert_to_int(num_buttons) for num_buttons in data_control_buttons.keys()]
            app.addSpinBoxRange('buttons', 0, max(converted_button_numbers))
            app.setSpinBoxPos('buttons', max(converted_button_numbers))
            app.setSpinBoxChangeFunction('buttons', partial(refresh_filtered_games, app))

        app.checkBox(title="clones", value=True, name="Include clones", row=2, column=2)
        app.setCheckBoxChangeFunction("clones", partial(refresh_filtered_games, app))

    refresh_filtered_games(app)


def setup_catver_filters_ui(app):
    catver_parser = configparser.ConfigParser()
    # The catver.ini file has some garbage at the top that will likely throw a parsing error.
    # TODO: distinguish between this state and when an actual problem has occurred
    try:
        catver_parser.read(app.getEntry('catver'))
    except configparser.ParsingError:
        pass
    catver = dict(catver_parser['Category'])
    for (game_name, category_string) in catver.items():
        categories = re.split(r'/|\*', category_string)
        categories = [category.strip() for category in categories]

        category = categories[0]
        if category != 'Quiz':
            if category not in data_categories:
                data_categories[category] = []
            data_categories[category].append(game_name)

        # Quiz games are probably better represented here as "Quiz game in X language"
        if category == 'Quiz':
            category = "Quiz: %s" % categories[1].split()[-1:][0]
            if category not in data_categories:
                data_categories[category] = []
            data_categories[category].append(game_name)

        if 'Mature' in categories:
            category = 'Mature'
            if category not in data_categories:
                data_categories[category] = []
            data_categories[category].append(game_name)
    print(data_categories)
    app.setSticky("nesw")
    app.startLabelFrame("Categories", row=3, column=0, colspan=3)
    i = 0
    for key in sorted(data_categories.keys()):
        app.checkBox(title="category_%s" % key, value=True, name=key, column=i % 4, row=int(i / 4))
        app.setCheckBoxChangeFunction("category_%s" % key, partial(refresh_filtered_games, app))
        i += 1
    app.stopLabelFrame()


def refresh_filtered_games(app):
    games = set(data_all_games)

    control_filters = [
        key
        for key in data_control_types.keys()
        if app.getCheckBox("control_%s" % key) is True
        ]
    games = filter_games(data_control_types, control_filters, games)

    button_filters = [
        str(num_buttons)
        for num_buttons in range(0, int(app.getSpinBox("buttons")))
        ]
    button_filters.append('None')
    games = filter_games(data_control_buttons, button_filters, games)

    emulation_filters = [
        key
        for key in data_driver_emulation.keys()
        if app.getCheckBox("emulation_%s" % key) is True
        ]
    games = filter_games(data_driver_emulation, emulation_filters, games)

    category_filters = [
        key
        for key in data_categories.keys()
        if app.getCheckBox("category_%s" % key) is True
        ]
    games = filter_games(data_categories, category_filters, games)

    if app.getCheckBox("clones") is False:
        games = games.difference(data_clones)

    data_filtered_games.clear()
    data_filtered_games.extend(games)
    app.setStatusbar("Number of Games: %d" % len(games), 0)


def setup_confirmation_page(app):
    app.startLabelFrame("Games to copy: %d" % len(data_filtered_games))
    app.setSticky('nsew')
    app.startScrollPane("gamelist-scrollpane")
    i = 0
    for game in data_filtered_games:
        app.addLabel(game, column=i % 7, row=int(i / 7))
        i += 1
        if i > 100:
            app.addLabel("...and %d more" % (len(data_filtered_games) - i))
            break
    app.stopScrollPane()
    app.stopLabelFrame()


def copy_files(app):
    total_files = len(data_filtered_games)
    app.setMeter("copy progress", 0)
    num_copied_files = 0
    from_dir = app.getEntry('rom_input_dir')
    to_dir = app.getEntry('rom_output_dir')
    skipped_games = []
    for game in data_filtered_games:
        if not path.exists(PurePath(from_dir, "%s.zip" % game)):
            skipped_games.append(game)
        else:
            copy2(PurePath(from_dir, "%s.zip" % game), PurePath(to_dir, "%s.zip" % game))
        num_copied_files += 1
        app.setMeter("copy progress", (num_copied_files / total_files) * 100)
        app.setLabel("now copying", "Now Copying: %s" % game)
    app.setLabel("now copying", "Done! Skipped copying these games: %s" % (' '.join(skipped_games)))


with gui(APP_NAME, "640x480") as app:
    def on_page_changed():
        page_number = app.getPagedWindowPageNumber(WINDOW_NAME)
        if page_number == 2:
            # Verify that we have an xml file present
            if app.getEntry("xml") == '':
                app.setPagedWindowPage(WINDOW_NAME, 1)
                return

            # Verify that we have a catver file present
            if app.getEntry("catver") == '':
                app.setPagedWindowPage(WINDOW_NAME, 1)
                return

            # Verify that we have an input ROMs directory
            if app.getEntry('rom_input_dir') == '':
                app.setPagedWindowPage(WINDOW_NAME, 1)
                return

            # Verify that we have an output ROMs directory
            if app.getEntry('rom_output_dir') == '':
                app.setPagedWindowPage(WINDOW_NAME, 1)
                return

            # Set up data and UI for the driver xml file
            setup_driver_xml_filters_ui(app)

            # Set up data and UI for the catver file
            setup_catver_filters_ui(app)
        if page_number == 3:
            setup_confirmation_page(app)
        if page_number == 4:
            copy_files(app)


    app.startPagedWindow(WINDOW_NAME)
    app.addStatusbar(fields=1)

    # Configuration
    app.startPage()
    app.setSticky('nsew')
    app.startLabelFrame("Input Parameters")
    app.setSticky('ew')
    app.label("mameXXX.xml")
    app.addFileEntry("xml")
    app.label("catver.ini")
    app.addFileEntry("catver")
    app.label("ROM directory")
    app.addDirectoryEntry("rom_input_dir")
    app.stopLabelFrame()

    app.startLabelFrame("Output Parameters")
    app.addDirectoryEntry("rom_output_dir")
    app.stopLabelFrame()
    app.stopPage()

    # Checkboxes
    app.startPage()
    app.stopPage()

    # Confirmation
    app.startPage()
    app.stopPage()

    # Copying files...
    app.startPage()
    app.addMeter("copy progress")
    app.setMeter("copy progress", 0)
    app.label("now copying", "Not started...")
    app.stopPage()

    app.setPagedWindowFunction(WINDOW_NAME, on_page_changed)

# TODO: refactor into smaller functions
