import os

import nuke
from PySide2.QtMultimedia import QSound

"""
This module notifies the user when rendering is finished by
playing a sound and displaying a notification.
"""

sound_file = QSound("{}/notify.wav".format(os.path.dirname(__file__)))


def notify_user():
    """
    Play sound and display notification when rendering is complete
    :return: None
    """

    sound_file.play()
    nuke.message("Rendering finished")
