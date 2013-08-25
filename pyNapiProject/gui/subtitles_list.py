from gi.repository import Gtk, GObject

class ColumnsConstants:
    SUBTITLES_ID = 0
    SUBTITLES_NAME = 1
    SUBTITLES_LANGUAGE = 2
    
class SubtitlesTreeView(Gtk.TreeView):
    def __init__(self, **kwargs):
        self.liststore = Gtk.ListStore(str, str, str)
        Gtk.TreeView.__init__(self, model = self.liststore, **kwargs)
        renderer_subtitles_subid = Gtk.CellRendererText()
        renderer_subtitles_name = Gtk.CellRendererText()
        renderer_subtitles_language = Gtk.CellRendererText()
        subtitles_id = Gtk.TreeViewColumn("Subtitles ID", renderer_subtitles_subid, text=0)
        subtitles_id.set_visible(False)
        subtitles_name = Gtk.TreeViewColumn("Subtitles Name", renderer_subtitles_name, text=1)
        subtitles_name.set_resizable(True)
        subtitles_name.set_min_width(400)
        subtitles_name.set_sort_column_id(ColumnsConstants.SUBTITLES_NAME)
        subtitles_language = Gtk.TreeViewColumn("Language", renderer_subtitles_language, text=2)
        subtitles_language.set_sort_column_id(ColumnsConstants.SUBTITLES_LANGUAGE)
        subtitles_language.set_resizable(True)
        subtitles_language.set_min_width(50)
        subtitles_language.set_max_width(100)
        self.set_grid_lines(3)
        self.append_column(subtitles_id)
        self.append_column(subtitles_name)
        self.append_column(subtitles_language)
    
        
    def display_subtitles(self, subtitles):
        self.liststore.clear()
        for subtitle in subtitles:
            self.liststore.append([subtitle.idsubtitlefile, subtitle.subfilename, subtitle.sublangid])
        
    def get_selected_subtitles(self):
        selection = self.get_selection()
        if not selection:
            return
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        tree_model, tree_iter = selection.get_selected()
        self.selected_user = tree_model.get_value(tree_iter, ColumnsConstants.SUBTITLES_ID)
        return self.selected_user
    