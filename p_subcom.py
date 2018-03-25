#-*- coding: UTF-8 -*-
import sublime, sublime_plugin
import subprocess
import os
import datetime

# [tag]
# #tag

# │name│/full_path│
# │name│@short_path│
# │name│~  command│

#---
# ecryptfs_subcom:
# /home/...
# ecryptfs_script_path = "/home/notus/Dropbox/Docs/python_scripts/ecryptfs/ecryptfs_thunar.py"

class subcom_main():
    def __init__(self):
        self.home_dir = "/home/notus/Se/"
        self.base_path = "/home/notus/Dropbox/Docs/Main/Base/base.sm"
        self.tag_subcom = "tag_subcom"
        self.name_subcom = "name_subcom"
        self.com_subcom = "com_subcom"
        self.path_subcom = "path_subcom"
        self.file_class = "file"
        self.sublime_project_file_ext = "sublime-project"
        self.video_file_ext = "video"
        self.music_file_ext  = "music"
        self.dir_class = "directory"
        self.error_path_class = "error_path"
        self.short_dict = {     "@notus": "/home/notus",
                                "@Dropbox": "@notus/Dropbox",
                                "@Docs": "@Dropbox/Docs",
                                "@Sublime Projects": "@Docs/Main/Sublime Projects",
                                "@User": "@notus/.config/sublime-text-3/Packages/User",
                                "@MEGA": "@notus/MEGA",
                                "@Seagate": "/media/notus/Seagate",
                                "@opt": "/opt",
                                "@usr": "/usr",
                                "@Конфиги": "@Docs/Конфиги",
                                "@Загрузки": "@notus/Загрузки" }

    def expand_path(self, short_path):
        if short_path[0] == "/":
            return short_path
        else:
            first_part, slash, last_part = short_path.partition("/")
            e = self.short_dict.get(first_part)
            if e == None: return short_path
            new_short_path = e + slash + last_part
            return self.expand_path(short_path = new_short_path)

    def class_of_subcom(self, subcom):
        class_of_subcom = "text"
        if subcom[0] in ['/', '@']:
            class_of_subcom = self.path_subcom
            subcom = self.expand_path(subcom)
        elif subcom[:2] == '~ ':
            class_of_subcom = self.com_subcom
            subcom = subcom[2:]
        return(class_of_subcom, subcom)

class POpenSubcomCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("expand_selection", {"to": "word"})
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            region = self.view.sel()[0]
            line = self.view.line(region)
            self.subcom_main = subcom_main()
            scope_name = self.view.scope_name(region.a)
            if scope_name == 'source.text_sm meta.name_subcom ':
                line_end = self.view.substr(sublime.Region(region.b, line.b))
                i_beg = line_end.index('│') + 1
                i_end = line_end.index('│', i_beg)
                subcom = line_end[i_beg:i_end]
                class_of_subcom, subcom_rev = self.subcom_main.class_of_subcom(subcom)
                line_beg = self.view.substr(sublime.Region(line.a, region.a))
                name = line_beg[line_beg.rfind('│') + 1:] + self.view.substr(region) + line_end[:i_beg-1]
                if class_of_subcom == self.subcom_main.com_subcom:
                    self.com_subcom_popup(name, class_of_subcom, subcom_rev)
                elif class_of_subcom == self.subcom_main.path_subcom:
                    if os.path.isdir(subcom_rev):
                        date = "[{0} {1}]".format(datetime.date.today().strftime("%d.%m.%Y"), datetime.datetime.now().strftime("%H:%M:%S"))
                        dirs_subcom = ['Folders: ' + date]
                        files_subcom = ['Files:   ' + date]
                        for i in os.listdir(subcom_rev):
                            i_path = os.path.join(subcom_rev, i)
                            if os.path.isdir(i_path):
                                dirs_subcom.append('│{0}│{1}│'.format(i, i_path))
                            if os.path.isfile(i_path):
                                files_subcom.append('│{0}│{1}│'.format(i, i_path))
                        level = self.view.indentation_level(region.a)
                        tabs = "\n{0}".format('\t' * (level + 1))
                        folders = tabs + tabs.join(dirs_subcom)
                        files = tabs + tabs.join(files_subcom)
                        tp = line.b + 1
                        while self.view.indentation_level(tp) != level: tp = self.view.full_line(tp).b
                        self.view.replace(edit, sublime.Region(line.b, tp - 1), folders + files)
                    elif os.path.isfile(subcom_rev):
                        if name[0] == '@':
                            f = open(subcom_rev, encoding='utf-8')
                            level = self.view.indentation_level(region.a)
                            date = "[{0} {1}]".format(datetime.date.today().strftime("%d.%m.%Y"), datetime.datetime.now().strftime("%H:%M:%S"))
                            tabs = "\n{0}".format('\t' * (level + 1))
                            text = tabs + date + tabs + tabs.join(f.read().split('\n'))
                            tp = line.b + 1
                            while self.view.indentation_level(tp) != level: tp = self.view.full_line(tp).b
                            self.view.replace(edit, sublime.Region(line.b, tp - 1), text)
                            f.close()
                        else:
                            self.path_subcom_popup(name, class_of_subcom, subcom_rev, subcom)
                    else:
                        body = '<b>Ошибка: </b>Несуществующий путь'
                        self.view.show_popup(body, max_width=1200, max_height=670, on_navigate=self.popup)
            elif 'meta.tag_subcom' in scope_name:
                self.tag_subcom_run(self.view.substr(region))

    def popup(self, href):
        class_of_subcom, subcom_rev = href.split("│")
        self.view.hide_popup()
        if class_of_subcom == self.subcom_main.name_subcom:
            self.run_name_subcom(subcom_rev)
        elif class_of_subcom == self.subcom_main.tag_subcom:
            self.run_tag(subcom_rev)
        elif class_of_subcom == self.subcom_main.com_subcom:
            subprocess.Popen(subcom_rev, shell=True)
        elif class_of_subcom in ['xfce4-terminal -x', 'xfce4-terminal -H -x']:
            subprocess.Popen(class_of_subcom + ' ' + subcom_rev, shell=True)
        elif class_of_subcom == self.subcom_main.path_subcom:
            self.run_path_subcom(subcom_rev)

    def tag_subcom_run(self, tag):
        # tag_mul = tag.split('*')
        tag_reg_list = self.view.find_all(r'(\[|\#| ){0}(\s|\]|\Z)'.format(tag))
        insert = '\n'.join(set([self.view.substr(self.view.line(i.a)).strip() for i in tag_reg_list]))
        new_view = self.new_tmp_tab('tag:' + tag)
        new_view.run_command("insert", {"characters": insert})
        new_view.set_viewport_position((0, 0))
        new_view.run_command("p_fold_subcom")

    def com_subcom_popup(self, name, class_of_subcom, subcom_rev):
        in_term_ico = '/home/notus/.config/sublime-text-3/Packages/Subcom/icons/in_term.png'
        in_term_no_exit_ico = '/home/notus/.config/sublime-text-3/Packages/Subcom/icons/in_term_no_exit.png'
        icons = '<a href="xfce4-terminal -x│{0}"><img src="file://{1}"></a><a href="xfce4-terminal -H -x│{0}"><img src="file://{2}"></a>'.format(subcom_rev, in_term_ico, in_term_no_exit_ico)
        head = '<div class="{0}">{1}:{2}</div>'.format(self.subcom_main.name_subcom, name, icons)
        body = '<a class="{0}" href="{0}│{1}">{1}</a>'.format(class_of_subcom, subcom_rev)
        html = self.generate_html(head, body)
        self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)

    def path_subcom_popup(self, name, class_of_subcom, subcom_rev, subcom):
        head = '<div class="{0}">{1}:</div>'.format(self.subcom_main.name_subcom, name)
        body = '<a class="{0}" href="{0}│{1}">{2}</a>'.format(class_of_subcom, subcom_rev, subcom)
        html = self.generate_html(head, body)
        self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)

    def run_path_subcom(self, path):
        root, ext = os.path.splitext(path)
        if ext == ".sublime-project":
            cmd = "/opt/sublime_text/sublime_text '{0}'; sleep 0.5; wmctrl -b add,maximized_vert,maximized_horz -r :ACTIVE:".format(path)
            subprocess.Popen(cmd, shell=True)
        if ext in [".mp3", ".mp4", ".webm", ".mkv", ".avi", ".jpg", ".png"]:
            subprocess.Popen("mpv '{0}'".format(path), shell=True)
        else:
            sublime.active_window().open_file(path) # , sublime.TRANSIENT

    def generate_html(  self,
                        head = "",
                        body = "",
                        tail = "", ):
        top = r'<body><style>a {text-decoration: underline} .tag {color: #787878} .name_subcom {color: #AC885B} .path_subcom {color: #416341} .com_subcom {color: #a31313}</style>'
        bot = '</body>'
        html = top + head + body + tail + bot
        return(html)

    def new_tmp_tab(self, name):
        new_view = sublime.active_window().new_file()
        new_view.set_syntax_file("Packages/Subcom/Subcom.sublime-syntax")
        new_view.set_name(name)
        return(new_view)