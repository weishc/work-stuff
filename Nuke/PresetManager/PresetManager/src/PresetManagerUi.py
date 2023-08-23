################################################################################
#
# PresetManager Ui module
#
################################################################################


import json
import os.path as op

import nuke

from . import PresetHelper
from . import config


def show_settings():
    """
    show settings window
    :return: None
    """

    settings = PresetHelper.load_settings()

    # create settings panel
    p = nuke.Panel("PresetManager settings")
    p.setWidth(600)
    p.addFilenameSearch("presets root: ", settings["presets_root"])

    if p.show():
        settings["presets_root"] = p.value("presets root: ")

        with open(config.PATH_SETTINGS_FILE, 'w') as sf:
            json.dump(settings, sf)

        # load presets
        PresetHelper.reload_presets_menu()


def show_about():
    """
    show settings window
    :return: None
    """

    info_file = op.normpath(op.join(op.dirname(__file__), "../", "data", "info.json"))

    if not op.isfile(info_file):
        nuke.message("PresetManager: info file doesn't exist")
        return

    with open(info_file) as f:
        info_data = json.load(f)

    logo = op.normpath(op.join(op.dirname(__file__), "../", "img", "logo.png"))
    nuke.message(
        "<img src='{}' style='float: right;' /><h1>PresetManager v{}</h1>\n\n{}".format(logo, info_data["version"],
                                                                                        info_data["info"]))


def add_preset():
    """
    create new preset by selected nodes
    :return: None
    """

    sel = nuke.selectedNodes()
    if len(sel) == 0:
        nuke.message("Please select some nodes to proceed.")
        return

    p = nuke.Panel("Add preset")
    p.setWidth(400)
    p.addSingleLineInput("Name: ", "")
    category_default = "---please_choose---"
    categories = PresetHelper.get_presets_categories(PresetHelper.load_settings()["presets_root"])
    categories.insert(0, category_default)
    p.addEnumerationPulldown("Category: ", " ".join(categories))

    if p.show():
        if p.value("Name: ") != "":
            if p.value("Category: ") != category_default:
                preset_full_path = op.join(PresetHelper.load_settings()["presets_root"], p.value("Category: "),
                                           "{}.nk".format(p.value("Name: ")))

                if op.isfile(preset_full_path):
                    if not nuke.ask(
                            "The preset '{0}' already exists. Do you want to overwrite it?".format(preset_full_path)):
                        return

                nuke.nodeCopy(preset_full_path)
                nuke.message("Succeessfully added preset '{0}/{1}'".format(p.value("Category: "), p.value("Name: ")))
                PresetHelper.reload_presets_menu()

            else:
                nuke.message("Please choose a category")
        else:
            nuke.message("Please enter a preset name")
