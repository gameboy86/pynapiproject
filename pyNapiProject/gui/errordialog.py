from gi.repository import Gtk

class ErrorDialog(Gtk.MessageDialog):
    def __init__(self, parent):
        Gtk.MessageDialog.__init__(self, parent, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL,"Some Errror")
        
    def _set_error_mesage(self, message):
        self.format_secondary_text(message)
    
    def show_error_dialog(self, message):
        self._set_error_mesage(message)
        self.run()
        self.destroy()