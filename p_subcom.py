#-*- coding: UTF-8 -*-
import sublime, sublime_plugin
import subprocess
import os
import webbrowser
import sys
import Subcom.subcom_core

# tag_subcom:
# [tag]

# name_subcom:
# │...│

# com_subcom:
# ~ ...│
# ~ -x ...│
# ~ -H -x ...│

# path_subcom:
# ~/...│
# ~...│

# dir_subcom:
# ~/.../│
# ~.../│

#---
# ecryptfs_subcom:
# /home/...

# ecryptfs_script_path = "/home/notus/Dropbox/Docs/python_scripts/ecryptfs/ecryptfs_thunar.py"

# all_meta = ["~", "-", "=", "f", "d", "p", "e", "t", "n"]

class POpenSubcomCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("expand_selection", {"to": "word"})
        if self.view.settings().get('syntax') == 'Packages/Subcom/Subcom.sublime-syntax':
            region = self.view.sel()[0]
            line = self.view.line(region)
            self.subcom_main = Subcom.subcom_core.subcom_main()
            if self.view.scope_name(region.a) == 'text.sm meta.name_subcom ':
                line_end = self.view.substr(sublime.Region(region.b, line.b))
                i_beg = line_end.find('│~')
                if i_beg == -1:
                    pass
                else:
                    line_end = line_end[i_beg + 1:]
                    i_end = line_end.find('│')
                    if i_end != -1:
                        subcom = line_end[:i_end + 1]
                        class_of_text, text = self.subcom_main.class_of_text(subcom)
                        html = self.generate_html(body='<a class="{0}" href="{0}\t{1}">{2}</a>'.format(class_of_text, text, subcom))
                        self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)
            else:
                line_beg = self.view.substr(sublime.Region(line.a, region.a))
                i_beg = max([line_beg.rfind(i) for i in ["│", "[", "~"]])
                # self.end = line.b
                if i_beg != -1:
                    line_end = self.view.substr(sublime.Region(region.b, line.b))
                    if line_beg[i_beg] == "│":
                        i_end = line_end.find("│")
                        if i_end != -1:
                            name = line_beg[i_beg+1:] + self.view.substr(region) + line_end[:i_end]
                            self.run_name_subcom(name)
                    elif line_beg[i_beg] == "[":
                        i_end = line_end.find("]")
                        if i_end != -1:
                            tag = self.view.substr(region)
                            self.run_tag(tag)
                    elif line_beg[i_beg] == "~":
                        i_end = line_end.find("│")
                        if i_end != -1:
                            subcom = line_beg[i_beg:] + self.view.substr(region) + line_end[:i_end+1]
                            class_of_text, text = self.subcom_main.class_of_text(subcom)
                            html = self.generate_html(body='<a class="{0}" href="{0}\t{1}">{2}</a>'.format(class_of_text, text, subcom))
                            self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)

    def popup(self, href):
        text_class, text = href.split("\t")
        self.view.hide_popup()
        if text_class == self.subcom_main.name_subcom:
            self.run_name_subcom(text)
        elif text_class == self.subcom_main.tag_subcom:
            self.run_tag(text)
        elif text_class == self.subcom_main.com_subcom:
            self.subcom_main.run_com_subcom(text)
        elif text_class == self.subcom_main.path_subcom:
            self.run_path_subcom(text)
        elif text_class == self.subcom_main.url_subcom:
            webbrowser.open_new_tab(text)

    def generate_html(  self,
                        top = r'''<body id="subcom"><style>a {text-decoration: none;} a.tag {color: #787878;} a.name_subcom {color: #AC885B;}
                        a.path_subcom {color: #5377a4;} a.com_subcom {color: #894d4d;}</style>''',
                        head = "",
                        body = "",
                        tail = "",
                        bot = '''</body>''' ):
        # self.head_html = head
        # self.body_html = body
        # self.tail_html = tail
        html = top + head + body + tail + bot
        return(html)

    def clear_html(self):
        self.head_html = ""
        self.tail_html = ""

    def two_column(self, in_list): #in main
        div, mod = divmod(len(in_list), 2)
        if mod: in_list.append("")
        height = div + mod
        out_list = []
        width = len(max(in_list[:height], key=len)) + 1
        for i in range(height):
            out_list.append(in_list[i].ljust(width, " ") + in_list[i+height])
        return(out_list)

    def new_tmp_tab(self, name):
        new_view = sublime.active_window().new_file()
        new_view.set_syntax_file("Packages/User/Subcom.sublime-syntax")
        new_view.set_name("tmp: " + name)
        return(new_view)

    def run_tag(self, exp):
        """ Обработчик тегов """
        out_list = self.subcom_main.tag_handler(exp)
        if out_list[0]:
            window = sublime.active_window()
            if window.num_groups() == 1:
                window.run_command('set_layout', {'cols': [0.0, 0.85, 1.0], 'rows': [0.0, 1.0], 'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]})
            
            window.focus_group(1)
            new_view = self.new_tmp_tab(exp)
            # new_view.run_command("insert", {"characters": "\n".join(self.two_column(out_list))})
            new_view.run_command("insert", {"characters": "\n".join(out_list)+"\n"})
            # new_view.run_command("toggle_setting", {"setting": "word_wrap"})
            window.focus_group(0)

            # self.view.run_command("insert", {"characters": exp+"\n"+"\n".join(self.two_column(out_list))+"\n"})
        else:
            self.view.show_popup("<b>Ошибка</b>: name_subcom по тегу {0} не найдено".format(exp))

    def run_name_subcom(self, text):
        """ Обработчик name_subcom """
        out_list = self.subcom_main.name_subcom_handler(text)
        # body = "<br>".join(['''<a class="{0}" href="{0}\t{1}">{2}</a>'''.format(self.subcom_main.class_of_text(i)[0], self.subcom_main.class_of_text(i)[1], i) for i in out_list])
        string_list = []
        for out in out_list:
            text_class, text_string = self.subcom_main.class_of_text(out)
            string_list.append('''<a class="{0}" href="{0}\t{1}">{2}</a>'''.format(text_class, text_string, out))
        body = "<br>".join(string_list)
        # head = self.head_html.split(" Page ")[0] + " <b>~│{0}│</b><br><br>".format(text)
        head = " <b>│{0}│</b><br>".format(text)
        html = self.generate_html(head=head, body=body)
        self.view.show_popup(html, max_width=1200, max_height=670, on_navigate=self.popup)

    def run_path_subcom(self, text):
        path_class, file_ext = self.subcom_main.class_of_path(text)
        if path_class == self.subcom_main.file_class:
            if file_ext == self.subcom_main.sublime_project_file_ext:
                cmd = "/opt/sublime_text/sublime_text '{0}'; sleep 0.5; wmctrl -b add,maximized_vert,maximized_horz -r :ACTIVE:".format(text)
                subprocess.Popen(cmd, shell=True)
            elif file_ext in [self.subcom_main.video_file_ext, self.subcom_main.music_file_ext]:
                self.subcom_main.run_com_subcom('mpv "{0}"'.format(text))
            else:
                sublime.active_window().open_file(text) # , sublime.TRANSIENT
        elif path_class == self.subcom_main.dir_class:
            # listdir = [i + "│" for i in os.listdir(text)] # new view
            # new_view = self.new_tmp_tab(text.split("/")[-2])
            # insert = text + "\n\n" + "\n".join(listdir)
            # new_view.run_command("insert", {"characters": insert}) #
            sublime.active_window().run_command("open_dir", {"dir": text})
        elif path_class == self.subcom_main.error_path_class:
            self.view.show_popup("<b>Ошибка</b>: Несуществующий путь:<br>{0}".format(text), max_width=1200)

#---
    def pages(self, list_of_string, string_num=30):
        page_html_list = []
        tail_html_list = []
        for page in range(0, len(list_of_string), string_num):
            html_list = []
            page_html = "<br>".join(['''<a class="{0}" href="{1}">{1}</a>'''.format(self.class_of_text(i), i) for i in list_of_string[page:page+string_num]])
            tail_html = '''<a class="page" href="page{0}">{0}</a>'''.format(page//string_num)
            page_html_list.append(page_html)
            tail_html_list.append(tail_html)
        return(page_html_list, tail_html_list)

    def sha1sum_in_path_subcom(self, sha1sum):
        """
        Переводит sha1sum в лист найденных path_subcom
        """
        path_subcom_list = []
        cmd = "cut -f 2,4 '{0}' | grep -F '{1}' | cut -f 2".format(self.bookmarks_path, sha1sum)
        out = subprocess.check_output(cmd, shell=True, universal_newlines=True).rstrip()
        if out: path_subcom_list = out.split("\n")
        return(path_subcom_list)
