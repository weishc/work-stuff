import nuke
import RenderFinishedNotification

nuke.addAfterRender(RenderFinishedNotification.notify_user)