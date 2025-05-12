# traycore.py
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, AppIndicator3, GLib

class TrayApp:
    def __init__(self, app_id, state, layout, icon='audio-x-generic'):
        self.icon = icon
        self.state = state
        self.layout = layout
        self.widgets = {}

        self.indicator = AppIndicator3.Indicator.new(
            app_id, icon,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        menu = Gtk.Menu()
        for item in layout:
            widget = self.build_item(item)
            if widget:
                menu.append(widget)
        menu.show_all()
        self.indicator.set_menu(menu)
        self.update_ui()

    def build_item(self, item):
        typ = item.get("type")

        if typ == "dynamic":
            label = item["template"].format(**self.state)
            w = Gtk.MenuItem(label=label)
            if "action" in item:
                w.connect("activate", lambda *_: item["action"]())
            self.widgets[item["id"]] = (w, item)
            return w

        if typ == "text":
            w = Gtk.MenuItem(label=self.state.get(item["bind"], ""))
            w.set_sensitive(False)
            self.widgets[item["id"]] = (w, item)
            return w

        if typ == "button":
            w = Gtk.MenuItem(label=item["label"])
            if "action" in item:
                w.connect("activate", lambda *_: item["action"]())
            self.widgets[item.get("id")] = (w, item)
            return w

        if typ == "toggle":
            w = Gtk.MenuItem()
            w.connect("activate", self._make_toggle_handler(item))
            self.widgets[item["id"]] = (w, item)
            return w

        if typ == "separator":
            return Gtk.SeparatorMenuItem()

        if typ == "submenu":
            container = Gtk.MenuItem(label=item["label"])
            submenu = Gtk.Menu()
            for subitem in item["build"]():
                sub = self._build_submenu_item(subitem)
                if sub:
                    submenu.append(sub)
            submenu.show_all()
            container.set_submenu(submenu)
            self.widgets[item["id"]] = (container, item)
            return container

        return None

    def _build_submenu_item(self, item, group):
        label = item["label"]
        if group is None:
            group_list = []
        else:
            group_list = group
        w = Gtk.RadioMenuItem.new_with_label(group_list, label)
        w.set_active(item.get("active", False))
        w.connect("activate", lambda _, fn=item["action"]: fn())
        group_list.append(w)
        return w, group_list


    def _make_toggle_handler(self, item):
        def handler(_):
            key = item["state"]
            index = 1 if self.state[key] else 0
            item["states"][index]["action"]()
        return handler

    def update_ui(self):
        for key, (widget, item) in self.widgets.items():
            typ = item.get("type")
            if typ == "text":
                widget.set_label(self.state.get(item["bind"], ""))
            elif typ == "toggle":
                index = 1 if self.state[item["state"]] else 0
                label = item["states"][index]["label"]
                widget.set_label(label)
            elif typ == "dynamic":
                label = item["template"].format(**self.state)
                widget.set_label(label)
        self.indicator.set_label(self.state.get("tray_label", ""), "")

    def rebuild_submenu(self, id, builder_fn):
        if id not in self.widgets:
            return
        container, item = self.widgets[id]
        new_menu = Gtk.Menu()
        entries = builder_fn()
        group = []
        for subitem in entries:
            w, group = self._build_submenu_item(subitem, group)
            if w:
                new_menu.append(w)
        new_menu.show_all()
        container.set_submenu(new_menu)

    def run(self, update_fn=None, interval=10):
        if update_fn:
            update_fn()
            GLib.timeout_add_seconds(interval, lambda: update_fn() or True)
        Gtk.main()

    def quit(self):
        Gtk.main_quit()
