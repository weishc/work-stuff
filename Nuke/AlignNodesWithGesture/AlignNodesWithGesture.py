import time

import nuke
from PySide2.QtGui import QCursor


def cur_mouse_pos():
    x_pos = QCursor.pos().x()
    y_pos = QCursor.pos().y()
    return x_pos, y_pos


def align_nodes(nodes, vertical=True):
    def avg(lst):
        return sum(lst) / len(lst)

    nuke.autoplace_snap_all()
    if vertical:
        avg_x = [n["xpos"].getValue() for n in nodes]
        for node in nodes:
            node.setXpos(int(avg(avg_x)))
    else:
        avg_y = [n["ypos"].getValue() for n in nodes]
        for node in nodes:
            node.setYpos(int(avg(avg_y)))


def wait_for_gesture(waiting_secs=3, interval=0.1, xform_threshold=150):
    slct = nuke.selectedNodes()
    if len(slct) < 2:
        return False
    current_sec = 0
    x = y = 0
    init_x, init_y = cur_mouse_pos()
    while waiting_secs > current_sec:
        x, y = cur_mouse_pos()
        if abs(x - init_x) > xform_threshold:
            align_nodes(slct, vertical=False)
            return True
        elif abs(y - init_y) > xform_threshold:
            align_nodes(slct, vertical=True)
            return True
        current_sec += interval
        time.sleep(0.1)
    return False
