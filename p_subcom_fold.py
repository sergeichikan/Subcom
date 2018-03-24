#-*- coding: UTF-8 -*-
import sublime, sublime_plugin

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