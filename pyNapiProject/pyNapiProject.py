from gui.main import MainWidnows
from gi.repository import Gtk, GObject


win = MainWidnows()
win.connect("delete-event", Gtk.main_quit)
Gtk.main()
