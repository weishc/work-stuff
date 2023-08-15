import os
import sys
import subprocess

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from PySide2.QtCore import QFile, QIODevice, QCoreApplication
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


class WeiFilePathEditor(QtCore.QObject):
    VERSION = "0.1.2"

    prompt_msgbox = QtCore.Signal(list)

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
            analysis.setdefault(img_root, {"exist": [], "missing": []})

            if img_exist:
                analysis[img_root]["exist"].append(node)
            else:
                analysis[img_root]["missing"].append(node)

        return analysis

    def get_all_file_nodes(self):
        return cmds.ls(type="file")

    def get_file_node_img_path(self, fnode):
        return cmds.getAttr("{0}.fileTextureName".format(fnode))

    def set_file_node_img_path(self, fnode, new_img_path):
        cmds.setAttr("{0}.fileTextureName".format(fnode), new_img_path, type="string")
        self.log_info(
            "Successfully set all selected textures to the target directory path"
        )

    def set_file_node_filter_type(self, fnode, option):
        cmds.setAttr("{0}.filterType".format(fnode), option)
        self.log_info("Successfully set filter type for all selected textures")

    def copy_move_files(
        self, source_fpaths, target_dir, progress_dialog, overwrite, copy=True
    ):
        progress_dialog.total_files = len(source_fpaths)
        for source_fpath in source_fpaths:
            fname = os.path.basename(source_fpath)
            target_fpath = os.path.join(target_dir, fname)
            if QFile.exists(target_fpath) and not overwrite:
                self.log_error(
                    "Target file already exists. Eanble overwrite to ignore."
                )
                progress_dialog.close()
                return

            source_file = QFile(source_fpath)
            target_file = QFile(target_fpath)

            progress_dialog.current_file += 1
            progress_dialog.update_progress_label()

            if not source_file.open(QIODevice.ReadOnly) or not target_file.open(
                QIODevice.WriteOnly
            ):
                raise IOError("Error opening files for copying.")

            total_size = source_file.size()
            bytes_copied = 0

            while bytes_copied < total_size:
                if progress_dialog.copy_cancelled:
                    break

                buffer = source_file.read(4096)
                target_file.write(buffer)
                bytes_copied += len(buffer)

                progress = float(bytes_copied) / float(total_size) * 100
                progress_dialog.progress_bar.setValue(progress)

                QCoreApplication.processEvents()

            if not copy:
                source_file.remove()

            source_file.close()
            target_file.close()

            if progress_dialog.copy_cancelled:
                progress_dialog.close()
            progress_dialog.cancel_button.setVisible(False)
            progress_dialog.close_button.setVisible(True)

    def log_error(self, text):
        self.prompt_msgbox.emit(["ERROR", text])

    def log_warning(self, text):
        self.prompt_msgbox.emit(["WARNING", text])

    def log_info(self, text):
        self.prompt_msgbox.emit(["INFO", text])


class WeiFilePathEditorFileProcessDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(WeiFilePathEditorFileProcessDialog, self).__init__(parent)

        self.setWindowTitle("File Processing Progress")
        self.file_process_layout = QtWidgets.QVBoxLayout()

        self.progress_label = QtWidgets.QLabel()
        self.file_process_layout.addWidget(self.progress_label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.file_process_layout.addWidget(self.progress_bar)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setVisible(True)
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.setVisible(False)
        self.file_process_layout.addWidget(self.cancel_button)
        self.file_process_layout.addWidget(self.close_button)

        self.setLayout(self.file_process_layout)

        self.total_files = None
        self.current_file = 0
        self.copy_cancelled = False

        self.cancel_button.clicked.connect(self.cancel_copy)
        self.close_button.clicked.connect(self.close)

    def update_progress_label(self):
        progress_text = "({0}/{1})".format(self.current_file, self.total_files)
        self.progress_label.setText(progress_text)

    def cancel_copy(self):
        self.copy_cancelled = True


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

    FILTER_TYPE_LIST = ["Off", "Mipmap", "Box", "Quardradic", "Quartic", "Gaussian"]

    IMGCVT_SUPPORT_FORMAT = [".jpg", ".png", ".gif", ".pic", ".tga", ".tif", ".tiff"]

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
            maya_main_window = wrapInstance(
                long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget
            )
        else:
            maya_main_window = wrapInstance(
                int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget
            )

        super(WeiFilePathEditorUi, self).__init__(maya_main_window)

        self.setWindowTitle(
            "{0} v{1}".format(WeiFilePathEditorUi.TITLE, WeiFilePathEditor.VERSION)
        )
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(450, 640)

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
        self.analyze_texture_btn = QtWidgets.QPushButton(
            "Analyze the texture path in this scene"
        )
        self.texture_analysis_tv = QtWidgets.QTreeView()
        self.texture_analysis_mdl = QtGui.QStandardItemModel()
        self.texture_analysis_tv.setModel(self.texture_analysis_mdl)
        self.texture_analysis_tv.setHeaderHidden(True)

        self.target_dir_le = QtWidgets.QLineEdit()
        self.target_dir_le.setPlaceholderText("Target Directory Path")

        self.target_dir_select_btn = QtWidgets.QPushButton("...")
        self.target_dir_select_btn.setFixedSize(24, 19)
        self.target_dir_select_btn.setToolTip("Select Target Directory")

        self.target_dir_show_folder_btn = QtWidgets.QPushButton(
            QtGui.QIcon(":fileOpen.png"), ""
        )
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

        self.filter_type_cmb = QtWidgets.QComboBox()
        self.filter_type_cmb.addItems(WeiFilePathEditorUi.FILTER_TYPE_LIST)
        self.filter_type_cmb.setCurrentText("Mipmap")
        self.set_filter_type_btn = QtWidgets.QPushButton("Set Filter Type")

        self.original_format_cmb = QtWidgets.QComboBox()
        self.original_format_cmb.addItem("*")
        self.original_format_cmb.addItems(WeiFilePathEditorUi.IMGCVT_SUPPORT_FORMAT)
        self.original_format_label = QtWidgets.QLabel("From")
        self.convert_format_cmb = QtWidgets.QComboBox()
        self.convert_format_cmb.addItems(WeiFilePathEditorUi.IMGCVT_SUPPORT_FORMAT)
        self.convert_format_label = QtWidgets.QLabel("To")
        self.update_texture_path_cb = QtWidgets.QCheckBox(
            "Update texture path in file nodes"
        )
        self.update_texture_path_cb.setChecked(True)
        self.delete_original_format_textures_cb = QtWidgets.QCheckBox(
            "Delete original format textures"
        )
        self.convert_format_btn = QtWidgets.QPushButton("Convert")

        self.main_tab.addTab(self.texture_tab, "Texture")
        self.main_tab.addTab(self.miscellaneous_tab, "Miscellaneous")

        self.copy_files_btn = QtWidgets.QPushButton("Copy Files")
        self.move_files_btn = QtWidgets.QPushButton("Move Files")
        self.set_texture_path_btn = QtWidgets.QPushButton("Set Texture Path")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        target_path_layout = QtWidgets.QHBoxLayout()
        target_path_layout.addWidget(self.target_dir_le)
        target_path_layout.addWidget(self.target_dir_select_btn)
        target_path_layout.addWidget(self.target_dir_show_folder_btn)

        make_new_folder_layout = QtWidgets.QHBoxLayout()
        make_new_folder_layout.addWidget(self.name_new_folder_le)
        make_new_folder_layout.addWidget(self.make_new_folder_cb)

        target_dir_layout = QtWidgets.QFormLayout()
        target_dir_layout.addWidget(self.force_overwrite_cb)
        target_dir_layout.addRow("Target Directory:", target_path_layout)
        target_dir_layout.addRow("Folder Name:", make_new_folder_layout)

        target_dir_grp = QtWidgets.QGroupBox("Target directory setting")
        target_dir_grp.setLayout(target_dir_layout)

        add_prefix_layout = QtWidgets.QHBoxLayout()
        add_prefix_layout.addWidget(self.add_prefix_cb)
        add_prefix_layout.addWidget(self.add_prefix_le)

        add_sufix_layout = QtWidgets.QHBoxLayout()
        add_sufix_layout.addWidget(self.add_sufix_cb)
        add_sufix_layout.addWidget(self.add_sufix_le)

        replace_string_layout = QtWidgets.QVBoxLayout()
        replace_string_layout.addWidget(self.replace_string_cb)
        replace_string_layout.addWidget(self.find_string_le)
        replace_string_layout.addWidget(self.replace_string_le)

        modify_texture_path_layout = QtWidgets.QVBoxLayout()
        modify_texture_path_layout.addLayout(add_prefix_layout)
        modify_texture_path_layout.addLayout(add_sufix_layout)
        modify_texture_path_layout.addLayout(replace_string_layout)
        modify_texture_path_grp = QtWidgets.QGroupBox("Modify Texture Path")
        modify_texture_path_grp.setLayout(modify_texture_path_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.copy_files_btn)
        button_layout.addWidget(self.move_files_btn)
        button_layout.addWidget(self.set_texture_path_btn)

        texture_tab_layout = QtWidgets.QVBoxLayout(self.texture_tab)
        texture_tab_layout.addWidget(self.analyze_texture_btn)
        texture_tab_layout.addWidget(self.texture_analysis_tv)
        texture_tab_layout.addWidget(target_dir_grp)
        texture_tab_layout.addWidget(modify_texture_path_grp)
        texture_tab_layout.addLayout(button_layout)

        set_filter_type_layout = QtWidgets.QHBoxLayout()
        set_filter_type_layout.addWidget(self.filter_type_cmb)
        set_filter_type_layout.addWidget(self.set_filter_type_btn)

        filter_type_layout = QtWidgets.QFormLayout()
        filter_type_layout.setSpacing(12)
        filter_type_layout.addRow("Filter Type", set_filter_type_layout)

        filter_type_grp = QtWidgets.QGroupBox('Filter setup (Maya "file" nodes only')
        filter_type_grp.setLayout(filter_type_layout)

        texture_format_conversion_layout = QtWidgets.QHBoxLayout()
        texture_format_conversion_layout.setSpacing(12)
        texture_format_conversion_layout.addWidget(self.original_format_label)
        texture_format_conversion_layout.addWidget(self.original_format_cmb)
        texture_format_conversion_layout.addWidget(self.convert_format_label)
        texture_format_conversion_layout.addWidget(self.convert_format_cmb)
        texture_format_conversion_layout.addWidget(self.convert_format_btn)
        texture_format_conversion_layout.addStretch()

        texture_format_conversion_button_layout = QtWidgets.QVBoxLayout()
        texture_format_conversion_button_layout.addWidget(self.update_texture_path_cb)
        texture_format_conversion_button_layout.addWidget(
            self.delete_original_format_textures_cb
        )
        texture_format_conversion_button_layout.addLayout(
            texture_format_conversion_layout
        )

        texture_format_conversion_grp = QtWidgets.QGroupBox(
            "Texture file format conversion"
        )
        texture_format_conversion_grp.setLayout(texture_format_conversion_button_layout)

        miscellaneous_tab_layout = QtWidgets.QVBoxLayout(self.miscellaneous_tab)
        miscellaneous_tab_layout.addWidget(filter_type_grp)
        miscellaneous_tab_layout.addWidget(texture_format_conversion_grp)
        miscellaneous_tab_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setMenuBar(self.main_menu)
        main_layout.addWidget(self.main_tab)
        main_layout.addLayout(texture_tab_layout)
        main_layout.addLayout(miscellaneous_tab_layout)
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
        self.copy_files_btn.clicked.connect(self.on_copy_move_files_btn)
        self.move_files_btn.clicked.connect(self.on_copy_move_files_btn)
        self.set_texture_path_btn.clicked.connect(self.on_set_texture_path_btn)

        self.set_filter_type_btn.clicked.connect(self.on_set_filter_type_btn)
        self.convert_format_btn.clicked.connect(self.on_convert_format)

        self.close_btn.clicked.connect(self.close)

        self._file_path_editor.prompt_msgbox.connect(self.show_msgbox_dlg)

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
                    missing_node_list += missing_r.data(QtCore.Qt.UserRole)
                continue
            row_value = row_item.data(QtCore.Qt.UserRole)
            exist_node_list += self._files_analysis_dict[row_value]["exist"]
            missing_node_list += self._files_analysis_dict[row_value]["missing"]

        return exist_node_list, missing_node_list

    def get_target_dir(self):
        return self.target_dir_le.text()

    def on_copy_move_files_btn(self):
        overwrite = self.force_overwrite_cb.isChecked()
        make_new_folder = self.make_new_folder_cb.isChecked()

        exist_node_list, _ = self.get_selected_treeview_item()
        if exist_node_list == []:
            self._file_path_editor.log_warning(
                "No existing node is selected, no texture is processed"
            )
            return

        target_dir = self.get_target_dir()
        if target_dir == "":
            self._file_path_editor.log_warning("Taget Directory is empty.")
            return
        if make_new_folder:
            new_folder_name = self.name_new_folder_le.text()
            target_dir = os.path.join(target_dir, new_folder_name)
            os.mkdir(target_dir)

        file_process_dlg = WeiFilePathEditorFileProcessDialog(self)
        file_process_dlg.show()
        source_fpaths = []
        for node in exist_node_list:
            fpath = self._file_path_editor.get_file_node_img_path(node)
            source_fpaths.append(fpath)

        if self.sender() == self.copy_files_btn:
            self._file_path_editor.copy_move_files(
                source_fpaths, target_dir, file_process_dlg, overwrite, copy=True
            )
        else:
            self._file_path_editor.copy_move_files(
                source_fpaths, target_dir, file_process_dlg, overwrite, copy=False
            )

    def on_set_texture_path_btn(self):
        add_prefix = self.add_prefix_cb.isChecked()
        add_sufix = self.add_sufix_cb.isChecked()
        replace_string = self.replace_string_cb.isChecked()

        target_dir = self.get_target_dir()
        exist_node_list, missing_node_list = self.get_selected_treeview_item()
        node_list = exist_node_list + missing_node_list
        for node in node_list:
            old_fpath = self._file_path_editor.get_file_node_img_path(node)
            fname = os.path.basename(old_fpath)

            if add_prefix:
                fname = self.add_prefix_le.text() + fname
            if add_sufix:
                fname = fname + self.add_sufix_le.text()
            if replace_string:
                fname = fname.replace(
                    self.find_string_le.text(), self.replace_string_le.text()
                )

            new_fpath = os.path.join(target_dir, fname)
            self._file_path_editor.set_file_node_img_path(node, new_fpath)

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
        new_dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", cur_dir_path
        )
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
            self.show_msgbox_dlg(
                ["ERROR", "Invalid directory path: {0}".format(target_dir_path)]
            )

    def toggle_make_new_folder_cb(self, state):
        self.name_new_folder_le.setEnabled(state == 2)

    def toggle_add_prefix_cb(self, state):
        self.add_prefix_le.setEnabled(state == 2)

    def toggle_add_sufix_cb(self, state):
        self.add_sufix_le.setEnabled(state == 2)

    def toggle_replace_string_cb(self, state):
        self.find_string_le.setEnabled(state == 2)
        self.replace_string_le.setEnabled(state == 2)

    def on_set_filter_type_btn(self):
        exist_node_list, missing_node_list = self.get_selected_treeview_item()
        node_list = exist_node_list + missing_node_list
        option = self.filter_type_cmb.currentIndex()
        for node in node_list:
            self._file_path_editor.set_file_node_filter_type(node, option)

    def on_convert_format(self):
        exist_node_list, _ = self.get_selected_treeview_item()
        imgcvt = os.path.join(os.getcwd(), "bin", "imgcvt.exe")

        update_to_fnode = self.update_texture_path_cb.isChecked()
        delete_original = self.delete_original_format_textures_cb.isChecked()
        original_format = self.original_format_cmb.currentText()
        convert_format = self.convert_format_cmb.currentText()

        for node in exist_node_list:
            fpath = self._file_path_editor.get_file_node_img_path(node)
            fname_with_ext = os.path.basename(fpath)
            fname, _ = os.path.splitext(fname_with_ext)
            target_dir = self.target_dir_le.text()
            output_fpath = os.path.join(target_dir, fname) + convert_format
            cmd = [imgcvt, fpath, output_fpath]
            if original_format != "*":
                cmd[1:1] = ["-f", original_format[1:]]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            finished = process.wait()
            if os.path.isfile(output_fpath):
                self._file_path_editor.log_info("Conversion sucess.")
                if delete_original:
                    os.remove(fpath)
                if update_to_fnode:
                    self._file_path_editor.set_file_node_img_path(node, output_fpath)
            else:
                self._file_path_editor.log_error(
                    "Conversion failed. Check the output log for more information."
                )

    def show_about_dialog(self):
        text = "<h2>{0}</h2>".format(WeiFilePathEditorUi.TITLE)
        text += "<p>Version: {0}</p>".format(WeiFilePathEditor.VERSION)
        text += "<p>Author: Wei-Hsiang Chen</p>"
        text += '<p>Website: <a style="color:white;" href="https://www.linkedin.com/in/weihsiangchen-fx">https://www.linkedin.com/in/weihsiangchen-fx</a></p><br>'

        QtWidgets.QMessageBox().information(self, "About", text)

    def show_msgbox_dlg(self, msg_type):
        dialog_type, text = msg_type
        if dialog_type == "ERROR":
            QtWidgets.QMessageBox().critical(self, "Error", text)
        elif dialog_type == "WARNING":
            QtWidgets.QMessageBox().warning(self, "Warning", text)
        else:
            QtWidgets.QMessageBox().information(self, "Info", text)


if __name__ == "__main__":
    try:
        wei_playblast_dialog.close()
        wei_playblast_dialog.deleteLater()
    except:
        pass

    wei_playblast_dialog = WeiFilePathEditorUi()
    wei_playblast_dialog.show()
