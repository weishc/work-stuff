################################################################################
#
# PresetManager helper module
#
################################################################################


import json
import os
import os.path as op

import nuke

from . import config


def reload_presets_menu():
    """
    reload presets dir and scan for new presets
    :return: None
    """

    old_all_presets = get_all_presets()
    load_presets()
    new_all_presets = get_all_presets()

    diff_list = [preset for preset in new_all_presets if preset not in old_all_presets]
    if diff_list:
        diff_preset = "\n".join(diff_list)
        nuke.message("{0} new presets found:\n\n{1}".format(len(diff_list), diff_preset))


def get_all_presets():
    """
    scan presets dir and get a list of all presets
    assert that all presets menus are uppercase
    :return: list of all presets
    """

    all_presets = []
    for item in nuke.menu("Nodes").findItem("PresetManager").items():
        if item.name().isupper():
            preset_menu = nuke.menu("Nodes").findItem("{0}/{1}".format("PresetManager", item.name()))
            try:
                for preset in preset_menu.items():
                    all_presets.append("{0}/{1}".format(preset_menu.name(), preset.name()))
            except:
                continue

    return all_presets


def load_presets(notify=False):
    """
    load presets from presets root dir
    :return: None
    """

    settings = load_settings()
    build_presets_menu(settings["presets_root"])


def load_settings():
    """
    load settings json
    create it if settings json doesn't exist
    :return: dict settings_data
    """

    # create missing json/dir
    settings_file = config.PATH_SETTINGS_FILE
    if not op.isdir(op.dirname(settings_file)):
        os.makedirs(op.dirname(settings_file))
    if not op.isfile(settings_file):
        with open(settings_file, "w") as f:
            f.write('{"presets_root": ""}')

    # load the settings json
    with open(settings_file, "r") as f:
        settings_data = json.load(f)

    return settings_data


def get_presets_categories(presets_root):
    """
    get a list of all preset categories
    scan the presets_root for dirs
    :param presets_root: string full path of presets root
    :return: list of all categories
    """

    if not op.isdir(presets_root):
        return []

    presets_categories = []
    for item in os.listdir(presets_root):
        item_full_path = op.join(presets_root, item)
        if op.isdir(item_full_path):
            presets_categories.append(item)

    return presets_categories


def build_presets_menu(presets_root):
    """
    scan presets_dir and build the presets menu
    :param presets_root: string full path of presets root
    :return: None
    """

    if not op.isdir(presets_root):
        if presets_root == "":
            nuke.message("PresetManager: presets_root not set. You can set it via 'PresetManager->settings'")
        else:
            nuke.message("PresetManager: presets_root '{0}' doesn't exist".format(presets_root))
        return

    pm_menu = nuke.menu("Nodes").findItem("PresetManager")

    preset_categories = get_presets_categories(presets_root)
    for category in preset_categories:
        category_menu = pm_menu.addMenu(category.upper())
        item_full_path = op.join(presets_root, category)
        for preset in os.listdir(item_full_path):
            if op.splitext(preset)[1] == ".nk":
                preset_path = op.join(item_full_path, preset)
                category_menu.addCommand(preset.replace(".nk", ""),
                                         lambda preset_path=preset_path: insert_preset(preset_path),
                                         icon="")


def insert_preset(presetpath):
    """
    insert preset to Nuke node graph
    :param presetpath: String full path of preset
    :return: None
    """

    if not op.isfile(presetpath):
        nuke.message("The preset cannot be found")
        return

    nuke.nodePaste(presetpath)
