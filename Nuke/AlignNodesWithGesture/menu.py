import nuke
import AlignNodesWithGesture

nuke.menu("Nuke").addCommand(
    "Wei's Toolbox/Align selected nodes with gesture",
    "AlignNodesWithGesture.wait_for_gesture()",
    "a",
)
