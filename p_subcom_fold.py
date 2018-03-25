#-*- coding: UTF-8 -*-
import sublime, sublime_plugin
import os

class PSubcomFoldViewListener(sublime_plugin.ViewEventListener):
    def on_activated(self):
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            self.view.run_command("p_fold_subcom")

    def on_selection_modified(self):
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            self.view.run_command("p_unfold_subcom_level")

class PFoldSubcomCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = self.view.find_by_selector('meta.fold_subcom')
        self.view.fold(regions)

        # tag_regs = self.view.find_by_selector('meta.tag_subcom') # find all tags

class PUnfoldSubcomLevelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        poi = self.view.sel()[0].a
        level = self.view.indentation_level(poi)
        next_line_poi = self.view.line(poi).b + 1
        next_line_level = self.view.indentation_level(next_line_poi)
        self.view.run_command("fold_by_level", {"level": level + 1})
        if next_line_level == level + 1:
            self.view.unfold(sublime.Region(next_line_poi))
            self.view.run_command("fold_by_level", {"level": level + 2})
            self.view.run_command("p_fold_subcom")

class PNameSubcomCaptionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass

    def find_name_subcom(self):
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            pt = self.view.sel()[0].a
            scope_name = self.view.scope_name(pt)
            if 'meta.name_subcom' in scope_name:
                return pt
        return False

    def get_subcom_name_value(self, pt):
        line = self.view.line(pt)
        line_beg = self.view.substr(sublime.Region(line.a, pt))
        line_end = self.view.substr(sublime.Region(pt, line.b))
        i_beg = line_beg.rindex('│')
        i_end = line_end.index('│')
        subcom_name = line_beg[i_beg + 1:] + line_end[:i_end]
        buf = line_end[i_end + 1:]
        i_end_end = buf.index('│')
        value = buf[:i_end_end]
        return (subcom_name, value)

    def is_visible(self):
        print('vis')
        if self.find_name_subcom(): return True
        return False

    def is_enabled(self):
        print('ena')
        return False

    def description(self):
        print('des')
        pt = self.find_name_subcom()
        if pt:
            subcom_name, path = self.get_subcom_name_value(pt)
            return subcom_name
        return 'Subcom'

class PNameSubcomCommand(sublime_plugin.TextCommand):
    def run(self, edit, com):
        pt = self.find_name_subcom()
        subcom_name, value = self.get_subcom_name_value(pt)
        if com == 'Rename':
            root_dir = os.path.dirname(value)
            new_path = os.path.join(root_dir, subcom_name)
            old_name = os.path.basename(value)
            text = 'Rename?\n\nDir:\n{0}\n\nName:\n{1}\n\nNew name:\n{2}'.format(root_dir, old_name, subcom_name)
            if sublime.ok_cancel_dialog(text):
                os.rename(value, new_path)
        elif com == 'Delete':
            root_dir = os.path.dirname(value)
            old_name = os.path.basename(value)
            text = 'Delete?\n\nDir:\n{0}\n\nName:\n{1}'.format(root_dir, old_name)
            if sublime.ok_cancel_dialog(text):
                os.remove(value)
        elif com == 'Open folder':
            sublime.active_window().run_command("open_dir", {"dir": value})
        elif com == 'Open file':
            sublime.active_window().open_file(value) # , sublime.TRANSIENT

    def get_subcom_name_value(self, pt):
        line = self.view.line(pt)
        line_beg = self.view.substr(sublime.Region(line.a, pt))
        line_end = self.view.substr(sublime.Region(pt, line.b))
        i_beg = line_beg.rindex('│')
        i_end = line_end.index('│')
        subcom_name = line_beg[i_beg + 1:] + line_end[:i_end]
        buf = line_end[i_end + 1:]
        i_end_end = buf.index('│')
        value = buf[:i_end_end]
        return (subcom_name, value)

    def is_visible(self, com):
        pt = self.find_name_subcom()
        if pt:
            if com == 'Open folder':
                subcom_name, value = self.get_subcom_name_value(pt)
                if os.path.isdir(value): return True
                return False
            elif com in ['Delete', 'Rename']:
                subcom_name, value = self.get_subcom_name_value(pt)
                if os.path.exists(value): return True
                return False
            elif com == 'Open file':
                subcom_name, value = self.get_subcom_name_value(pt)
                if os.path.isfile(value): return True
                return False
            else:
                return True
        else:
            return False

    def find_name_subcom(self):
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            # pt = self.view.window_to_text((event["x"], event["y"]))
            pt = self.view.sel()[0].a
            scope_name = self.view.scope_name(pt)
            if 'meta.name_subcom' in scope_name:
                return pt
        return False