import nuke

"""
This module can create a read node from a selected write node
"""

def create_read_from_write():
    """
    Create a read node from a selected write node
    :return: None
    """

    slct = nuke.selectedNode()

    if slct.Class() == "Write":
        read = nuke.createNode("Read")
        read.setXpos(int(slct["xpos"].getValue()))
        read.setYpos(int(slct["ypos"].getValue()+50))
        read["file"].setValue(slct["file"].getValue())
        read["first"].setValue(int(nuke.Root()["first_frame"].getValue()))
        read["last"].setValue(int(nuke.Root()["last_frame"].getValue()))
        read["origfirst"].setValue(int(nuke.Root()["first_frame"].getValue()))
        read["origlast"].setValue(int(nuke.Root()["last_frame"].getValue()))
        read["colorspace"].setValue(int(slct["colorspace"].getValue()))
