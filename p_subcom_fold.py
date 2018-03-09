#-*- coding: UTF-8 -*-
import sublime, sublime_plugin
# import subprocess
# import os
# import webbrowser

class PSubcomFoldViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = self.view.find_all(r'~.*?│')
        regions_n = [sublime.Region(region.a, region.b-1) for region in regions]
        self.view.fold(regions_n)

    # def on_activated(self):
    #     print('mod')
        # pat = r'│.*?│~.*?│'
        # self.view.fold(self.view.find_all(r'~.*?│'))