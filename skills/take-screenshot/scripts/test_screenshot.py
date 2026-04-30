
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GdkPixbuf
import os

def take_screenshot(x, y, w, h, filename):
    window = Gdk.get_default_root_window()
    if not window:
        print("No root window found")
        return False
    pb = Gdk.pixbuf_get_from_window(window, x, y, w, h)
    if not pb:
        print("Failed to get pixbuf")
        return False
    pb.savev(filename, "png", [], [])
    print(f"Screenshot saved to {filename}")
    return True

take_screenshot(0, 0, 3072, 1728, "tmp-screenshots/gdk_left.png")
take_screenshot(3072, 0, 1728, 3072, "tmp-screenshots/gdk_right.png")
