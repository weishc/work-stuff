import nuke
import ReadFromWrite

nuke.menu("Nuke").addCommand(
    "Wei's Toolbox/Read from write", "ReadFromWrite.create_read_from_write()", "alt+r"
)
