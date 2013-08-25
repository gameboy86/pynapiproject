from gi.repository import Gtk, GObject
from .subtitles_list import SubtitlesTreeView
from .errordialog import ErrorDialog
from opentsubtitles.subtitles import FileProperties, SubtitlesSearchProperties, SubtitlesConncector,\
    NoSubtitlesError, FileNotExistError

class MainWidnows(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title = 'PyNapiProject')
        self._set_windows_properties()
        self._add_buttons()
        self.subtitle_connector = SubtitlesConncector(user_name = '', password = '')
        self.frame1 = Gtk.Frame()
        self.frame1.set_label("Search:")
        self.vbox = Gtk.Box(spacing = 6, orientation = Gtk.Orientation.VERTICAL)
        self.hbox = Gtk.Box(spacing = 6, orientation = Gtk.Orientation.HORIZONTAL)
        self.buttonsBox = Gtk.Box(spacing = 1, orientation = Gtk.Orientation.VERTICAL)
        
        self.add(self.vbox)

        self.file_path_label = Gtk.Entry()
        self.file_path_label.set_text('Brak')
        self.chose_movie_button.connect('clicked', self.chose_file)
        self.find_subtitles_button.connect('clicked', self.find_subtitles)
        self.get_subtitle_button.connect('clicked', self.download_subtitles)
        self.treeview = SubtitlesTreeView()
        scrollTree = Gtk.ScrolledWindow()
        scrollTree.set_hexpand(True)
        scrollTree.set_vexpand(True)
        scrollTree.add(self.treeview)
        self.frame1.add(self.hbox)
        self.status_bar = Gtk.Statusbar()
        self.context_id = self.status_bar.get_context_id( "Statusbar example")
        self.status_bar.push( self.context_id, "")
        self.vbox.pack_start(self.frame1, False, True, 0)
        self.vbox.pack_start(scrollTree, False, True, 0)
        self.vbox.pack_start(self.status_bar, False, True, 0)
        self.hbox.pack_start(self.file_path_label, True, True, 0)
        self.hbox.pack_start(self.buttonsBox, True, True, 0)
        self.hbox.pack_start(self.get_subtitle_button, True, True, 0)
        self.buttonsBox.pack_start(self.chose_movie_button, False, True, 0)
        self.buttonsBox.pack_start(self.find_subtitles_button, False, True, 0)
        self.show_all()
        self.treeview.connect('cursor-changed', self.get_selected_subtitles)
        
        
    def _add_buttons(self):
        self.chose_movie_button = Gtk.Button(label = "Chose Movie", stock =  Gtk.STOCK_OPEN)
        self.find_subtitles_button = Gtk.Button(label = "Find Subtitles")
        self.get_subtitle_button = Gtk.Button(label = "Download")
        self._set_buttons_properties()
    
    def _set_buttons_properties(self):
        self.get_subtitle_button.set_sensitive(False)
        self.find_subtitles_button.set_size_request(100,10)
        
    def _set_windows_properties(self):
        self.set_default_size(600, 300)
    
    def get_selected_subtitles(self, widget):
        self.subid = self.treeview.get_selected_subtitles()
        if self.subtitles:
            self.to_download_subtitles = self.subtitles.search_by_id(self.subid)
        else:
            return
        self.get_subtitle_button.set_sensitive(True)

    def download_subtitles(self, widget):
        if self.to_download_subtitles:
            self.subtitle_connector.get_subtitles(self.to_download_subtitles)
        else:
            return
   
    def find_subtitles(self, widget):
        try:
            f = FileProperties(self.file_path_label.get_text())
            file_size = f.get_file_size()
            file_hash = f.get_file_hash()
            subtitles = SubtitlesSearchProperties(moviebytesize = file_size, moviehash = file_hash)
        except FileNotExistError as e:
            self.error_dialog = ErrorDialog(self)
            self.error_dialog.show_error_dialog(e.args[0])
            self.status_bar.push(self.context_id, "Find: 0 subtitles")
            return
        try:
            self.subtitles = self.subtitle_connector.search_subtitles(subtitles)
            self.treeview.display_subtitles(self.subtitles)
            self.status_bar.push(self.context_id, "Find: {0} subtitles".format(len(self.subtitles)))
        except NoSubtitlesError as e:
            self.treeview.liststore.clear()
            self.error_dialog = ErrorDialog(self)
            self.error_dialog.show_error_dialog(e.args[0])
            self.status_bar.push(self.context_id, "Find: 0 subtitles")
            
    def chose_file(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file_path_label.set_text(str(dialog.get_filename()))
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

