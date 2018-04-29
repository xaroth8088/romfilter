import xml.etree.ElementTree as ET

from appJar import gui


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
data_num_players = {}
data_driver_emulation = {}


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
        elif game_inputs[0].get('players') is None:
            print('ERROR:', name, 'did not specify a number of players')
            print(game_inputs[0])
        else:
            num_players = game_inputs[0].get('players')
            add_game_to_data(data_num_players, num_players, name)

            if int(num_players) > 0:
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
    print('players:')
    print(data_num_players.keys())
    print('emulation:')
    print(data_driver_emulation.keys())


def safe_convert_to_int(number_string):
    try:
        return int(number_string)
    except ValueError:
        return 0


with gui("ROM Filter", "640x480") as app:
    def on_page_changed():
        page_number = app.getPagedWindowPageNumber("Data Files")
        if page_number == 2:
            # Verify that we have an xml file present
            if app.getEntry("xml") is None:
                app.setPagedWindowPage("Data Files", 1)
                return

            get_filters(app.getEntry('xml'))

            app.setSticky("new")
            app.startLabelFrame("Control Types", row=0, column=0, colspan=2)
            i = 0
            for key in data_control_types.keys():
                app.addCheckBox(title="control_%s" % key, name=key, column=i % 3, row=int(i / 3))
                app.setCheckBox("control_%s" % key, True)
                i += 1
            app.stopLabelFrame()

            app.startLabelFrame("Emulation Status", row=0, column=2)
            for key in data_driver_emulation.keys():
                app.addCheckBox(title="emulation_%s" % key, name=key)
                app.setCheckBox("emulation_%s" % key, True)
            app.stopLabelFrame()

            app.setSticky("")
            app.startLabelFrame("Max Buttons", row=1, column=0)
            converted_button_numbers = [safe_convert_to_int(num_buttons) for num_buttons in data_control_buttons.keys()]
            app.addSpinBoxRange('buttons', 0, max(converted_button_numbers))
            app.stopLabelFrame()

            app.startLabelFrame("Max Players", row=1, column=1)
            converted_player_numbers = [safe_convert_to_int(num_players) for num_players in data_num_players.keys()]
            app.addSpinBoxRange('players', 0, max(converted_player_numbers))
            app.stopLabelFrame()

            app.addCheckBox(title="clones", name="allow clones", row=1, column=2)
            app.setCheckBox("clones", True)

            # TODO: catver


    app.startPagedWindow("Data Files")

    app.startPage()
    app.label("mameXXX.xml")
    app.addFileEntry("xml")
    app.label("catver.ini (optional)")
    app.addFileEntry("catver")
    app.stopPage()

    app.startPage()
    app.stopPage()

    app.setPagedWindowFunction("Data Files", on_page_changed)

# main()

# TODO: optionally include the genres from catver.ini as another way to filter
# TODO: refactor into smaller functions
