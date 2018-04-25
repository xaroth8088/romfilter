import xml.etree.ElementTree as ET

from appJar import gui


# parser = argparse.ArgumentParser(description='Filter MAME Roms')
# parser.add_argument('--xml', metavar='FILE', type=str,
#                     help='path to the MAME full driver information, in XML format')
# parser.add_argument('--destination', metavar='DESTINATION_PATH', type=str, nargs=1,
#                     help='where to copy filtered roms')
# parser.add_argument('--dry', action='store_true',
#                     help='Dry Run - just output what would be done, without moving any files')
# parser.add_argument('--list-filters', action='store_true',
#                     help='List the available filters')
# parser.add_argument('--exclude-clones', action='store_true',
#                     help="Don't include any clones")
# parser.add_argument('--include-control-type', type=str, nargs='*',
#                     help='specify a control type to include')
# parser.add_argument('--include-buttons', type=str, nargs='*',
#                     help='include games with this many buttons')
# parser.add_argument('--include-ways', type=str, nargs='*',
#                     help='include games with this many axes on the controller')
# parser.add_argument('--include-players', type=str, nargs='*',
#                     help='include games that support up to this many players')
# parser.add_argument('--include-status', type=str, nargs='*',
#                     help='include games with this driver status')
# parser.add_argument('--include-emulation', type=str, nargs='*',
#                     help='include games with this level of emulation')
# parser.add_argument('--include-savestate', type=str, nargs='*',
#                     help='include games with this level of savestate support')


# args = parser.parse_args()


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


def filter_games(store, include_list, games):
    if include_list is None or len(include_list) == 0:
        return games

    filtered_games = games

    excluded_criteria = set(store.keys()).difference(set(include_list))
    for criteria in excluded_criteria:
        filtered_games = filtered_games.difference(store[criteria])

    return filtered_games


data_all_games = []
data_clones = []
data_control_types = {}
data_control_buttons = {}
data_control_ways = {}
data_num_players = {}
data_driver_status = {}
data_driver_emulation = {}
data_driver_savestate = {}


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
                    add_game_to_data(data_control_types, extract_control_attribute(game_controls, 'type'), name)
                    add_game_to_data(data_control_buttons, extract_control_attribute(game_controls, 'buttons'), name)
                    add_game_to_data(data_control_ways, extract_control_attribute(game_controls, 'ways'), name)

        game_driver = machine.findall('driver')
        if game_driver is None or len(game_driver) == 0:
            print('ERROR:', name, 'did not have an <driver> specified')
        elif len(game_driver) > 1:
            print('ERROR:', name, 'had too many <driver> elements specified')
        else:
            add_game_to_data(data_driver_status, game_driver[0].get('status'), name)
            add_game_to_data(data_driver_emulation, game_driver[0].get('emulation'), name)
            add_game_to_data(data_driver_savestate, game_driver[0].get('savestate'), name)

    print('clones')
    print('control-type:')
    print(data_control_types.keys())
    print('buttons:')
    print(data_control_buttons.keys())
    print('ways:')
    print(data_control_ways.keys())
    print('players:')
    print(data_num_players.keys())
    print('status:')
    print(data_driver_status.keys())
    print('emulation:')
    print(data_driver_emulation.keys())
    print('savestate:')
    print(data_driver_savestate.keys())


# def main():
#     data_all_games = []
#     data_clones = []
#     data_control_types = {}
#     data_control_buttons = {}
#     data_control_ways = {}
#     data_num_players = {}
#     data_driver_status = {}
#     data_driver_emulation = {}
#     data_driver_savestate = {}
#
#     tree = ET.parse(args.xml)
#     machines = tree.findall('machine')
#
#     for machine in machines:
#         name = machine.get('name')
#         if machine.get('runnable') == 'no':
#             continue
#         print('processing', name, end="\r")
#
#         data_all_games.append(name)
#
#         if machine.get('cloneof') is not None:
#             data_clones.append(name)
#
#         game_inputs = machine.findall('input')
#         if game_inputs is None or len(game_inputs) == 0:
#             print('ERROR:', name, 'did not have an <input> specified')
#         elif len(game_inputs) > 1:
#             print('ERROR:', name, 'had too many <input> elements specified')
#         elif game_inputs[0].get('players') is None:
#             print('ERROR:', name, 'did not specify a number of players')
#             print(game_inputs[0])
#         else:
#             num_players = game_inputs[0].get('players')
#             add_game_to_data(data_num_players, num_players, name)
#
#             if int(num_players) > 0:
#                 game_controls = game_inputs[0].findall('control')
#                 if game_controls is None or len(game_controls) == 0:
#                     add_game_to_data(data_control_types, 'None', name)
#                 else:
#                     add_game_to_data(data_control_types, extract_control_attribute(game_controls, 'type'), name)
#                     add_game_to_data(data_control_buttons, extract_control_attribute(game_controls, 'buttons'), name)
#                     add_game_to_data(data_control_ways, extract_control_attribute(game_controls, 'ways'), name)
#
#         game_driver = machine.findall('driver')
#         if game_driver is None or len(game_driver) == 0:
#             print('ERROR:', name, 'did not have an <driver> specified')
#         elif len(game_driver) > 1:
#             print('ERROR:', name, 'had too many <driver> elements specified')
#         else:
#             add_game_to_data(data_driver_status, game_driver[0].get('status'), name)
#             add_game_to_data(data_driver_emulation, game_driver[0].get('emulation'), name)
#             add_game_to_data(data_driver_savestate, game_driver[0].get('savestate'), name)
#
#     if args.list_filters is True:
#         print('clones')
#         print('control-type:')
#         print(data_control_types.keys())
#         print('buttons:')
#         print(data_control_buttons.keys())
#         print('ways:')
#         print(data_control_ways.keys())
#         print('players:')
#         print(data_num_players.keys())
#         print('status:')
#         print(data_driver_status.keys())
#         print('emulation:')
#         print(data_driver_emulation.keys())
#         print('savestate:')
#         print(data_driver_savestate.keys())
#         return
#
#     filtered_games = set(data_all_games)
#
#     if args.exclude_clones is True:
#         filtered_games = filtered_games.difference(data_clones)
#
#     filtered_games = filter_games(data_control_types, args.include_control_type, filtered_games)
#     filtered_games = filter_games(data_control_buttons, args.include_buttons, filtered_games)
#     filtered_games = filter_games(data_control_ways, args.include_ways, filtered_games)
#     filtered_games = filter_games(data_num_players, args.include_players, filtered_games)
#     filtered_games = filter_games(data_driver_status, args.include_status, filtered_games)
#     filtered_games = filter_games(data_driver_emulation, args.include_emulation, filtered_games)
#     filtered_games = filter_games(data_driver_savestate, args.include_savestate, filtered_games)
#
#     print(len(filtered_games), "games are included:")
#     print(filtered_games)


with gui("ROM Filter", "640x480") as app:
    def on_page_changed():
        page_number = app.getPagedWindowPageNumber("Data Files")
        if page_number == 2:
            # Verify that we have an xml file present
            if app.getEntry("xml") is None:
                app.setPagedWindowPage("Data Files", 1)
                return

            get_filters(app.getEntry('xml'))
            app.startLabelFrame("Control Types")
            app.startScrollPane("types-pane")
            for key in data_control_types.keys():
                app.addCheckBox(title="control_%s" % key, name=key)
                app.setCheckBox("control_%s" % key, True)
            app.stopScrollPane()
            app.stopLabelFrame()

            app.startLabelFrame("Number of Buttons")
            app.startScrollPane("buttons-pane")
            # TODO: For this one, use a number input of some sort to pick the minimum and maximum number of buttons,
            # TODO: then, when filtering, autogenerate the appropriate entries
            for key in data_control_buttons.keys():
                app.addCheckBox(title="buttons_%s" % key, name=key)
                app.setCheckBox("buttons_%s" % key, True)
            app.stopScrollPane()
            app.stopLabelFrame()

            app.startLabelFrame("Joystick Directions")
            app.startScrollPane("ways-pane")
            for key in data_control_ways.keys():
                app.addCheckBox(title="ways_%s" % key, name=key)
                app.setCheckBox("ways_%s" % key, True)
            app.stopScrollPane()
            app.stopLabelFrame()

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
# TODO: GUI, instead of CLI
