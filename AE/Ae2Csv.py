import os.path as op
import csv
import xmltodict

from PySide2.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QWidget,
    QComboBox,
    QLineEdit,
    QFormLayout,
)

FILE_FILTERS = [
    "Fianl Cut Pro XML (*.xml)",
    "All files (*)",
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AE to CSV")

        layout = QFormLayout()

        self.fps_cbb = QComboBox()
        layout.addRow("FPS:", self.fps_cbb)
        self.fps_cbb.addItems(
            [
                "",
                "8",
                "12",
                "15",
                "23.976",
                "24",
                "25",
                "29.97",
                "30",
                "50",
                "59.94",
                "60",
                "120",
            ]
        )
        self.fps_cbb.resize(500, 50)

        open_xml_btn = QPushButton("Open XML files")
        open_xml_btn.clicked.connect(self.get_filenames)
        layout.addRow(open_xml_btn)

        self.xml_path_pte = QPlainTextEdit()
        self.xml_path_pte.setReadOnly(True)
        layout.addRow("XML paths:", self.xml_path_pte)
        # xml_path_pte.insertPlainText("You\n can write text here")

        slct_output_btn = QPushButton("Select output folder")
        slct_output_btn.clicked.connect(self.get_folder)
        layout.addRow(slct_output_btn)

        self.output_path_le = QLineEdit()
        layout.addRow("Output folder path:", self.output_path_le)

        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self.write_csv)
        layout.addRow(convert_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def get_filenames(self):
        caption = ""  # Empty uses default caption.
        initial_dir = ""  # Empty uses current folder.
        initial_filter = FILE_FILTERS[0]  # Select one from the list.
        filters = ";;".join(FILE_FILTERS)

        (
            fname_list,
            selected_filter,
        ) = QFileDialog.getOpenFileNames(
            self,
            caption=caption,
            directory=initial_dir,
            filter=filters,
            initialFilter=initial_filter,
        )
        for xml in fname_list:
            last_xml_fps = self.read_xml_fps(xml)
            if not last_xml_fps:
                self.fps_cbb.setCurrentIndex(0)
                self.xml_path_pte.setPlainText("")
                return
        fnames = "\n".join(fname_list)
        self.xml_path_pte.setPlainText(fnames)
        self.fname_list = fname_list
        xml_fps_idx = self.fps_cbb.findText(last_xml_fps)
        self.fps_cbb.setCurrentIndex(xml_fps_idx)

    def get_folder(self):
        caption = ""  # Empty uses default caption.
        initial_dir = ""  # Empty uses current folder.
        folder_path = QFileDialog.getExistingDirectory(
            self,
            caption=caption,
            directory=initial_dir,
        )
        self.output_path_le.setText(folder_path)

    def frames_to_TC(self, frames):
        # h = int(frames / fps**60)
        fps = float(self.fps_cbb.currentText())
        m = int(frames / (fps * 60)) % 60
        s = int((frames % (fps * 60)) / fps)
        f = int(frames % (fps * 60) % fps)
        # return ( "%02d:%02d:%02d:%02d" % ( h, m, s, f))
        return "{:02d}:{:02d}:{:02d}".format(m, s, f)

    def frames_to_second(self, frames):
        # h = int(frames / fps**60)
        fps = float(self.fps_cbb.currentText())
        m = int(frames / (fps * 60)) % 60
        s = int((frames % (fps * 60)) / fps)
        f = int(frames % (fps * 60) % fps)
        # return ( "%02d:%02d:%02d:%02d" % ( h, m, s, f))
        second = "{}秒{}格".format(s, f)
        if m > 0:
            second = "{}分{}".format(m, second)
        return second

    def read_xml_fps(self, fpath):
        try:
            with open(fpath) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())
            fps = data_dict["xmeml"]["sequence"]["rate"]["timebase"]
            return fps
        except KeyError:
            with open(fpath) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())
            fps = data_dict["xmeml"]["project"]["children"]["clip"]["rate"]["timebase"]
            return fps
        except:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Invalid XML format")
            dlg.setText(f"Invalid XML format.\nError XML:{fpath}")
            dlg.exec_()
            return False

    def read_xml(self, fpath):
        check_list = ["generatoritem", "clipitem"]
        with open(fpath) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
        tracks_data = data_dict["xmeml"]["sequence"]["media"]["video"]["track"]
        row_list = []
        if type(tracks_data) is list:
            for tracks in tracks_data:
                item_list = [i for i in tracks.keys() if i in check_list]
                for item in item_list:
                    if type(tracks[item]) is list:
                        for track in tracks[item]:
                            row_list.append(self.track_to_row(track))
                    else:
                        row_list.append(self.track_to_row(tracks[item]))
        else:
            item_list = [i for i in tracks_data.keys() if i in check_list]
            for item in item_list:
                if type(tracks_data[item]) is list:
                    for track in tracks_data[item]:
                        row_list.append(self.track_to_row(track))
                else:
                    row_list.append(self.track_to_row(tracks_data[item]))
        return row_list

    def track_to_row(self, track):
        start_frame = int(track["start"])
        end_frame = int(track["end"])
        cut_duration = end_frame - start_frame
        time_in = self.frames_to_TC(start_frame + 1)
        time_out = self.frames_to_TC(end_frame)
        duration_TC = self.frames_to_second(cut_duration)
        row = [
            track["name"],
            time_in,
            time_out,
            duration_TC,
            start_frame + 1,
            end_frame,
            cut_duration,
        ]
        return row

    def write_csv(self):
        for xml in self.fname_list:
            row_list = self.read_xml(xml)
            fname = op.basename(xml).split(".")[0] + ".csv"
            output_fpath = op.join(self.output_path_le.text(), fname)
            with open(output_fpath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "NO",
                        "段落",
                        "time in",
                        "time out",
                        "秒數",
                        "frame in",
                        "frame out",
                        "cut duration",
                    ]
                )

                def sort_list(row):
                    return row[2]

                row_list.sort(key=sort_list)
                for idx, row in enumerate(row_list):
                    writer.writerow([idx + 1] + row)
            if op.exists(output_fpath):
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Success!")
                dlg.setText("Convert success!")
                dlg.exec_()
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Failed!")
                dlg.setText("Convert failed!")
                dlg.exec_()


app = QApplication([])

window = MainWindow()
window.resize(500, 200)
window.show()

app.exec_()
