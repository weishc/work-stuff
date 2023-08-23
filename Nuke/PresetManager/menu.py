import os.path as op

import nuke

import PresetManager.src.PresetHelper as helper
import PresetManager.src.PresetManagerUi as pmui

logo = op.normpath(op.join(op.dirname(__file__), "PresetManager", "img", "logo.png"))

# build menu
pm_menu = nuke.menu("Nodes").addMenu("PresetManager", icon=logo)
pm_menu.addCommand("reload", helper.reload_presets_menu)
pm_menu.addCommand("add nodes preset", pmui.add_preset)
pm_menu.addCommand("settings", pmui.show_settings)
pm_menu.addCommand("about", pmui.show_about)
pm_menu.addSeparator()

helper.load_presets()
