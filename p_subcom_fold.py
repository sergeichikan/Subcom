#-*- coding: UTF-8 -*-
import sublime, sublime_plugin

class PSubcomFoldViewListener(sublime_plugin.ViewEventListener):
    def on_activated(self):
        self.view.run_command("p_subcom_fold")

        # regions = self.view.find_all(r'│.*?│~.*?│')

        # self.view.fold([sublime.Region(region.a, region.b-1) for region in regions])


class PSubcomFoldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = self.view.find_by_selector('meta.fold_subcom')
        self.view.fold(regions)