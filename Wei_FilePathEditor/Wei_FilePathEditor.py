import copy
import os
import sys
import traceback

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


class WeiFilePathEditor(QtCore.QObject):
    VERSION = "0.0.1"

    output_logged = QtCore.Signal(str)
    output_error_warning = QtCore.Signal(list)

    def __init__(self, ffmpeg_path=None, log_to_maya=True):
        super(WeiFilePathEditor, self).__init__()
               
    def get_project_dir_path(self):
        return cmds.workspace(q=True, rootDirectory=True)
        
    def analyze_texture(self):
        analysis = {}
        
        for node in self.get_all_file_nodes():
            img_path = self.get_file_node_img_path(node)
            img_exist = os.path.exists(img_path)
            img_root = os.path.dirname(img_path)
            analysis.setdefault(img_root,{'exist':[],'missing':[]})
            
            if img_exist:
                analysis[img_root]['exist'].append(node)
            else:
                analysis[img_root]['missing'].append(node)
        
        return analysis
            
        
    def get_all_file_nodes(self):
        return cmds.ls(type="file")
            
    def get_file_node_img_path(self, fnode):
        return cmds.getAttr("{0}.fileTextureName".format(fnode))
        
    def set_file_node_img_path(self, fnode, new_img_path):
        cmds.setAttr("{0}.fileTextureName".format(fnode), new_img_path, type="string")

    def log_error(self, text):
        if self._log_to_maya:
            om.MGlobal.displayError("[WeiFilePathEditor] {0}".format(text))

        self.output_logged.emit("[ERROR] {0}".format(text))
        self.output_error_warning.emit(["ERROR",text])
        
    def log_warning(self, text):
        if self._log_to_maya:
            om.MGlobal.displayWarning("[WeiFilePathEditor] {0}".format(text))

        self.output_logged.emit("[WARNING] {0}".format(text))
        self.output_error_warning.emit(["WARNING",text])
        
    def log_output(self, text):
        if self._log_to_maya:
            om.MGlobal.displayInfo(text)

        self.output_logged.emit(text)


class WeiFilePathEditorUi(QtWidgets.QDialog):
    TITLE = "Wei's File Path Editor"
    
    STYLESHEET = """
            QTreeView {
                background-color: #454545;
            }
            QLineEdit:disabled {
                background-color: #454545;
            }
        """

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = WeiFilePathEditorUi()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self):
        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        else:
            maya_main_window = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

        super(WeiFilePathEditorUi, self).__init__(maya_main_window)

        self.setWindowTitle("{0} v{1}".format(WeiFilePathEditorUi.TITLE, WeiFilePathEditor.VERSION))
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(450,640)

        self.setStyleSheet(WeiFilePathEditorUi.STYLESHEET)

        self._file_path_editor = WeiFilePathEditor()
        self._files_analysis_dict = None
 
        self.create_actions()
        self.create_menus()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
    def create_actions(self):
        self.show_about_action = QtWidgets.QAction("About", self)
        self.show_about_action.triggered.connect(self.show_about_dialog)

    def create_menus(self):
        self.main_menu = QtWidgets.QMenuBar()

        about_menu = self.main_menu.addMenu("About")
        about_menu.addAction(self.show_about_action)

    def create_widgets(self):
        self.main_tab = QtWidgets.QTabWidget()
        
        self.texture_tab = QtWidgets.QWidget()
        self.analyze_texture_btn = QtWidgets.QPushButton("Analyze the texture path in this scene")
        self.texture_analysis_tv = QtWidgets.QTreeView()
        self.texture_analysis_mdl = QtGui.QStandardItemModel()
        self.texture_analysis_tv.setModel(self.texture_analysis_mdl)
        self.texture_analysis_tv.setHeaderHidden(True)
        
        self.target_dir_le = QtWidgets.QLineEdit()
        self.target_dir_le.setPlaceholderText("Target Directory Path")
        
        self.target_dir_select_btn = QtWidgets.QPushButton("...")
        self.target_dir_select_btn.setFixedSize(24, 19)
        self.target_dir_select_btn.setToolTip("Select Target Directory")
        
        self.target_dir_show_folder_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self.target_dir_show_folder_btn.setFixedSize(24, 19)
        self.target_dir_show_folder_btn.setToolTip("Show in Folder")
        
        self.force_overwrite_cb = QtWidgets.QCheckBox("Force Overwrite")
        self.make_new_folder_cb = QtWidgets.QCheckBox("Make New Folder")
        self.name_new_folder_le = QtWidgets.QLineEdit()
        self.name_new_folder_le.setEnabled(False)
        self.name_new_folder_le.setPlaceholderText("New folder")
        
        self.add_prefix_cb = QtWidgets.QCheckBox("Add Prefix to Filename")
        self.add_prefix_le = QtWidgets.QLineEdit()
        self.add_prefix_le.setEnabled(False)
        self.add_prefix_le.setPlaceholderText("prefix_")
        
        self.add_sufix_cb = QtWidgets.QCheckBox("Add Sufix to Filename")
        self.add_sufix_le = QtWidgets.QLineEdit()
        self.add_sufix_le.setEnabled(False)
        self.add_sufix_le.setPlaceholderText("_sufix")
        
        self.replace_string_cb = QtWidgets.QCheckBox("Replace String")
        self.find_string_le = QtWidgets.QLineEdit()
        self.find_string_le.setEnabled(False)
        self.find_string_le.setPlaceholderText("Old String")
        self.replace_string_le = QtWidgets.QLineEdit()
        self.replace_string_le.setPlaceholderText("New String")
        self.replace_string_le.setEnabled(False)
        
        self.miscellaneous_tab = QtWidgets.QWidget()
        
        self.main_tab.addTab(self.texture_tab, "Texture")
        self.main_tab.addTab(self.miscellaneous_tab, "Miscellaneous")
        
        self.copy_files_btn = QtWidgets.QPushButton("Copy Files")
        self.move_files_btn = QtWidgets.QPushButton("Move Files")
        self.set_texture_path_btn = QtWidgets.QPushButton("Set Texture Path")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_layout(self):
        target_path_layout = QtWidgets.QHBoxLayout()
        target_path_layout.setSpacing(8)
        target_path_layout.addWidget(self.target_dir_le)
        target_path_layout.addWidget(self.target_dir_select_btn)
        target_path_layout.addWidget(self.target_dir_show_folder_btn)
        
        make_new_folder_layout = QtWidgets.QHBoxLayout()
        make_new_folder_layout.setSpacing(8)
        make_new_folder_layout.addWidget(self.name_new_folder_le)
        make_new_folder_layout.addWidget(self.make_new_folder_cb)
        make_new_folder_layout.addWidget(self.force_overwrite_cb)
        
        target_dir_layout = QtWidgets.QFormLayout()
        target_dir_layout.setSpacing(8)
        target_dir_layout.addRow("Target Directory:", target_path_layout)
        target_dir_layout.addRow("Folder Name:", make_new_folder_layout)
        
        add_prefix_layout = QtWidgets.QHBoxLayout()
        add_prefix_layout.addSpacing(8)
        add_prefix_layout.addWidget(self.add_prefix_cb)
        add_prefix_layout.addWidget(self.add_prefix_le)
        
        add_sufix_layout = QtWidgets.QHBoxLayout()
        add_sufix_layout.addSpacing(8)
        add_sufix_layout.addWidget(self.add_sufix_cb)
        add_sufix_layout.addWidget(self.add_sufix_le)

        replace_string_layout = QtWidgets.QVBoxLayout()
        replace_string_layout.addSpacing(8)
        replace_string_layout.addWidget(self.replace_string_cb)
        replace_string_layout.addWidget(self.find_string_le)
        replace_string_layout.addWidget(self.replace_string_le)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.copy_files_btn)
        button_layout.addWidget(self.move_files_btn)
        button_layout.addWidget(self.set_texture_path_btn)
        
        texture_tab_layout = QtWidgets.QVBoxLayout(self.texture_tab)
        texture_tab_layout.addWidget(self.analyze_texture_btn)
        texture_tab_layout.addWidget(self.texture_analysis_tv)
        texture_tab_layout.addLayout(target_dir_layout)
        texture_tab_layout.addLayout(add_prefix_layout)
        texture_tab_layout.addLayout(add_sufix_layout)
        texture_tab_layout.addLayout(replace_string_layout)
        texture_tab_layout.addLayout(button_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        main_layout.setMenuBar(self.main_menu)
        main_layout.addWidget(self.main_tab)
        main_layout.addLayout(texture_tab_layout)
        main_layout.addWidget(self.close_btn)

    def create_connections(self):
        self.analyze_texture_btn.clicked.connect(self.create_hierarchy)
        
        self.target_dir_select_btn.clicked.connect(self.select_target_dir)
        self.target_dir_show_folder_btn.clicked.connect(self.open_target_dir)
        
        self.make_new_folder_cb.stateChanged.connect(self.toggle_make_new_folder_cb)
        self.add_prefix_cb.stateChanged.connect(self.toggle_add_prefix_cb)
        self.add_sufix_cb.stateChanged.connect(self.toggle_add_sufix_cb)
        self.replace_string_cb.stateChanged.connect(self.toggle_replace_string_cb)
        
        self.texture_analysis_mdl.itemChanged.connect(self.disable_child_item)
        self.copy_files_btn.clicked.connect(self.on_copy_files_btn)
        self.move_files_btn.clicked.connect(self.on_move_files_btn)
        self.set_texture_path_btn.clicked.connect(self.on_set_texture_path_btn)
                
        self.close_btn.clicked.connect(self.close)
        
    def create_hierarchy(self):
        self._files_analysis_dict = self._file_path_editor.analyze_texture()
        if self.texture_analysis_mdl.rowCount() > 0:
            self.clean_treeview(self.texture_analysis_mdl)

        for key, exist_dict in self._files_analysis_dict.items():
            total = 0
            for i in exist_dict.values():
                total += len(i)
                
            key_item = QtGui.QStandardItem("{0} texture(s) in {1}".format(total, key))
            key_item.setCheckable(True)
            key_item.setData(key, QtCore.Qt.UserRole)
            self.texture_analysis_mdl.appendRow(key_item)

            for k, v in exist_dict.items():
                item = QtGui.QStandardItem("{0} of them {1}".format(len(v), k))
                item.setCheckable(True)
                item.setData(v, QtCore.Qt.UserRole)
                key_item.appendRow(item)
                
    def get_selected_treeview_item(self):
        treeview = self.texture_analysis_mdl
        exist_node_list = []
        missing_node_list = []
        for row in range(treeview.rowCount()):
            row_item = treeview.item(row, 0)
            row_selected = row_item.checkState()
            if not row_selected:
                exist_r = row_item.child(0)
                if exist_r.checkState():
                    exist_node_list += exist_r.data(QtCore.Qt.UserRole)
                missing_r = row_item.child(1)
                if missing_r.checkState():
                     missing_node_list +=  missing_r.data(QtCore.Qt.UserRole)
                continue
            row_value = row_item.data(QtCore.Qt.UserRole)
            exist_node_list += self._files_analysis_dict[row_value]['exist']
            missing_node_list += self._files_analysis_dict[row_value]['missing']
        
        return exist_node_list, missing_node_list
        
    def on_copy_files_btn(self):
        exist_node_list, _ = self.get_selected_treeview_item()

    def on_move_files_btn(self):
        exist_node_list, _ = self.get_selected_treeview_item()
        
    def on_set_texture_path_btn(self):
        exist_node_list, missing_node_list = self.get_selected_treeview_item()
        node_list = exist_node_list + missing_node_list
        
    def clean_treeview(self, treeview):
        for row in range(treeview.rowCount()):
            treeview.removeRow(0)
            
    def disable_child_item(self, item):
        row_count = item.rowCount()
        if row_count == 0:
            return
        if item.checkState() == 0:
            for r in range(row_count):
                r_child = item.child(r)
                r_child.setEnabled(True)
            return
        for r in range(row_count):
            r_child = item.child(r)
            r_child.setData(False, QtCore.Qt.CheckStateRole)
            r_child.setEnabled(False)

    def select_target_dir(self):
        cur_dir_path = self._file_path_editor.get_project_dir_path()
        new_dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", cur_dir_path)
        if new_dir_path:
            self.target_dir_le.setText(new_dir_path)

    def open_target_dir(self):
        target_dir_path = self.target_dir_le.text()
        if not target_dir_path:
            return

        file_info = QtCore.QFileInfo(target_dir_path)
        if file_info.isDir():
            QtGui.QDesktopServices.openUrl(target_dir_path)
        else:
            self.show_error_warning_dialog(["ERROR","Invalid directory path: {0}".format(target_dir_path)])
                
    def toggle_make_new_folder_cb(self, state):
        self.name_new_folder_le.setEnabled(state == 2)

    def toggle_add_prefix_cb(self, state):
        self.add_prefix_le.setEnabled(state == 2)
        
    def toggle_add_sufix_cb(self, state):
        self.add_sufix_le.setEnabled(state == 2)
        
    def toggle_replace_string_cb(self, state):
        self.find_string_le.setEnabled(state == 2)
        self.replace_string_le.setEnabled(state == 2)

    def show_about_dialog(self):
        text = '<h2>{0}</h2>'.format(WeiFilePathEditorUi.TITLE)
        text += '<p>Version: {0}</p>'.format(WeiFilePathEditor.VERSION)
        text += '<p>Author: Wei-Hsiang Chen</p>'
        text += '<p>Website: <a style="color:white;" href="https://www.linkedin.com/in/weihsiangchen-fx">https://www.linkedin.com/in/weihsiangchen-fx</a></p><br>'

        QtWidgets.QMessageBox().information(self, "About", text)

    def show_error_warning_dialog(self, error_or_warning):
        dialog_type, text = error_or_warning
        if dialog_type == "ERROR":
            QtWidgets.QMessageBox().critical(self, "Error", text)
        else:
            QtWidgets.QMessageBox().warning(self, "Warning", text)

if __name__ == "__main__":


    try:
        wei_playblast_dialog.close()
        wei_playblast_dialog.deleteLater()
    except:
        pass

    wei_playblast_dialog = WeiFilePathEditorUi()
    wei_playblast_dialog.show()




