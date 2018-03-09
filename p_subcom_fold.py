#-*- coding: UTF-8 -*-
import sublime, sublime_plugin
# import subprocess
# import os
# import webbrowser

class PSubcomFoldViewCommand(sublime_plugin.ViewEventListener):
    def on_activated(self):
        # regions = self.view.find_all(r'│.*?│~.*?│')
        regions = self.view.find_by_selector('meta.fold_subcom')

        # self.view.fold([sublime.Region(region.a, region.b-1) for region in regions])
        self.view.fold(regions)

    # def on_activated(self):
    #     print('mod')
        # pat = r'│.*?│~.*?│'
        # self.view.fold(self.view.find_all(r'~.*?│'))