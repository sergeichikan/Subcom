#-*- coding: UTF-8 -*-
import sublime, sublime_plugin
import subprocess
import os
import webbrowser
import sys
import Subcom.subcom_core

# tag_subcom:
# [tag]

#---
# ecryptfs_subcom:
# /home/...

# ecryptfs_script_path = "/home/notus/Dropbox/Docs/python_scripts/ecryptfs/ecryptfs_thunar.py"

# │name│/full_path│
# │name│@short_path│
# │name│~  command│

class POpenSubcomCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("expand_selection", {"to": "word"})
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            region = self.view.sel()[0]
            line = self.view.line(region)
            self.subcom_main = Subcom.subcom_core.subcom_main()
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
                    self.path_subcom_popup(name, class_of_subcom, subcom_rev, subcom)
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
        elif class_of_subcom == 'open_dir':
            sublime.active_window().run_command("open_dir", {"dir": subcom_rev})

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
        open_dir_icon = '/home/notus/.config/sublime-text-3/Packages/Subcom/icons/open_dir.png'
        icons = '<a href="open_dir│{0}"><img src="file://{1}"></a>'.format(subcom_rev, open_dir_icon)
        head = '<div class="{0}">{1}: {2}</div>'.format(self.subcom_main.name_subcom, name, icons)
        body = '<a class="{0}" href="{0}│{1}">{2}</a>'.format(class_of_subcom, subcom_rev, subcom)
        html = self.generate_html(head, body)
        self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)

    def generate_html(  self,
                        head = "",
                        body = "",
                        tail = "", ):
        top = r'<body><style>a {text-decoration: underline} .tag {color: #787878} .name_subcom {color: #AC885B} .path_subcom {color: #416341} .com_subcom {color: #a31313}</style>'
        bot = '</body>'
        html = top + head + body + tail + bot
        return(html)

    def run_path_subcom(self, path):
        path_class, file_ext = self.subcom_main.class_of_path(path)
        if path_class == self.subcom_main.file_class:
            if file_ext == self.subcom_main.sublime_project_file_ext:
                cmd = "/opt/sublime_text/sublime_text '{0}'; sleep 0.5; wmctrl -b add,maximized_vert,maximized_horz -r :ACTIVE:".format(path)
                subprocess.Popen(cmd, shell=True)
            elif file_ext in [self.subcom_main.video_file_ext, self.subcom_main.music_file_ext]:
                subprocess.Popen("mpv '{0}'".format(path), shell=True)
            else:
                sublime.active_window().open_file(path) # , sublime.TRANSIENT
        elif path_class == self.subcom_main.dir_class:
            if path[-1] == '/': path = path[:-1]
            dirs_subcom = []
            files_subcom = []
            for i in os.listdir(path):
                # name, ext = os.path.splitext(i)
                # name.rfind('[')
                i_path = os.path.join(path, i)
                if os.path.isdir(i_path):
                    dirs_subcom.append('│{0}│{1}│'.format(i+'/', i_path))
                if os.path.isfile(i_path):
                    files_subcom.append('│{0}│{1}│'.format(i, i_path))
            root_dirs = []
            head, tail = os.path.split(path)
            while tail:
                root_dirs.append('│{0}│{1}│'.format(tail, os.path.join(head, tail)))
                head, tail = os.path.split(head)
            root_dirs.reverse()
            insert = ' / '.join(root_dirs) + '\n\n' + "\n".join(dirs_subcom) + '\n\n' + "\n".join(files_subcom)
            new_view = self.new_tmp_tab('dir:' + os.path.basename(path))
            new_view.run_command("insert", {"characters": insert})
            tag_regions = new_view.find_all(r'\[.+?\]')
            new_view.set_viewport_position((0, 0))
            new_view.run_command("p_fold_subcom")
        elif path_class == self.subcom_main.error_path_class:
            self.view.show_popup("<b>Ошибка</b>: Несуществующий путь:<br>{0}".format(path), max_width=1200)

    # def two_column(self, in_list): #in main
    #     div, mod = divmod(len(in_list), 2)
    #     if mod: in_list.append("")
    #     height = div + mod
    #     out_list = []
    #     width = len(max(in_list[:height], key=len)) + 1
    #     for i in range(height):
    #         out_list.append(in_list[i].ljust(width, " ") + in_list[i+height])
    #     return(out_list)

    def new_tmp_tab(self, name):
        new_view = sublime.active_window().new_file()
        new_view.set_syntax_file("Packages/Subcom/Subcom.sublime-syntax")
        new_view.set_name(name)
        return(new_view)

    # def run_tag(self, exp):
    #     """ Обработчик тегов """
    #     out_list = self.subcom_main.tag_handler(exp)
    #     if out_list[0]:
    #         window = sublime.active_window()
    #         if window.num_groups() == 1:
    #             window.run_command('set_layout', {'cols': [0.0, 0.85, 1.0], 'rows': [0.0, 1.0], 'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]})
            
    #         window.focus_group(1)
    #         new_view = self.new_tmp_tab(exp)
    #         # new_view.run_command("insert", {"characters": "\n".join(self.two_column(out_list))})
    #         new_view.run_command("insert", {"characters": "\n".join(out_list)+"\n"})
    #         # new_view.run_command("toggle_setting", {"setting": "word_wrap"})
    #         window.focus_group(0)

    #         # self.view.run_command("insert", {"characters": exp+"\n"+"\n".join(self.two_column(out_list))+"\n"})
    #     else:
    #         self.view.show_popup("<b>Ошибка</b>: name_subcom по тегу {0} не найдено".format(exp))

    # def run_name_subcom(self, text):
    #     """ Обработчик name_subcom """
    #     out_list = self.subcom_main.name_subcom_handler(text)
    #     # body = "<br>".join(['''<a class="{0}" href="{0}\t{1}">{2}</a>'''.format(self.subcom_main.class_of_text(i)[0], self.subcom_main.class_of_text(i)[1], i) for i in out_list])
    #     string_list = []
    #     for out in out_list:
    #         text_class, text_string = self.subcom_main.class_of_text(out)
    #         string_list.append('<a class="{0}" href="{0}\t{1}">{2}</a>'.format(text_class, text_string, out))
    #     body = "<br>".join(string_list)
    #     # head = self.head_html.split(" Page ")[0] + " <b>~│{0}│</b><br><br>".format(text)
    #     head = " <b>│{0}│</b><br>".format(text)
    #     html = self.generate_html(head=head, body=body)
    #     self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)

#---
    # def pages(self, list_of_string, string_num=30):
    #     page_html_list = []
    #     tail_html_list = []
    #     for page in range(0, len(list_of_string), string_num):
    #         html_list = []
    #         page_html = "<br>".join(['''<a class="{0}" href="{1}">{1}</a>'''.format(self.class_of_text(i), i) for i in list_of_string[page:page+string_num]])
    #         tail_html = '''<a class="page" href="page{0}">{0}</a>'''.format(page//string_num)
    #         page_html_list.append(page_html)
    #         tail_html_list.append(tail_html)
    #     return(page_html_list, tail_html_list)

    # def sha1sum_in_path_subcom(self, sha1sum):
    #     """
    #     Переводит sha1sum в лист найденных path_subcom
    #     """
    #     path_subcom_list = []
    #     cmd = "cut -f 2,4 '{0}' | grep -F '{1}' | cut -f 2".format(self.bookmarks_path, sha1sum)
    #     out = subprocess.check_output(cmd, shell=True, universal_newlines=True).rstrip()
    #     if out: path_subcom_list = out.split("\n")
    #     return(path_subcom_list)
