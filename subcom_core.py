import subprocess
import os.path

class subcom_main():
    def __init__(self):
        self.home_dir = "/home/notus/Se/"
        self.base_path = "/home/notus/Dropbox/Docs/Main/Base/base.sm"
        self.tag_subcom = "tag_subcom"
        self.name_subcom = "name_subcom"
        self.com_subcom = "com_subcom"
        self.path_subcom = "path_subcom"
        self.url_subcom = "url_subcom"
        self.file_class = "file"
        self.sublime_project_file_ext = "sublime-project"
        self.video_file_ext = "video"
        self.music_file_ext  = "music"
        self.dir_class = "directory"
        self.error_path_class = "error_path"
        self.short_dict = {     "notus": "/home/notus",
                                "Dropbox": "notus/Dropbox",
                                "Docs": "Dropbox/Docs",
                                "Sublime Projects": "Docs/Main/Sublime Projects",
                                "User": "notus/.config/sublime-text-3/Packages/User",
                                "MEGA": "notus/MEGA",
                                "Seagate": "/media/notus/Seagate",
                                "opt": "/opt",
                                "usr": "/usr",
                                "Конфиги": "Docs/Конфиги",
                                "Загрузки": "notus/Загрузки" }

    def expand_path(self, short_path):
        if short_path[0] == "/":
            return short_path
        else:
            first_part, slash, last_part = short_path.partition("/")
            e = self.short_dict.get(first_part)
            if e == None: return short_path
            new_short_path = e + slash + last_part
            return self.expand_path(short_path = new_short_path)

    def class_of_text(self, text):
        text_class = "text"
        if text:
            if text[0] == "[" and text[-1] == "]":
                text_class = self.tag_subcom
                text = text[1:-1]
            elif text[:4] == "http":
                text_class = self.url_subcom
            elif text[-1] == "│":
                text = text[:-1]
                if text[0] == "│":
                    text_class = self.name_subcom
                    text = text[1:]
                elif text[0] == "~":
                    text = text[1:]
                    if text[0] == " ":
                        text_class = self.com_subcom
                        text = text[1:]
                        if text[:6] == "-H -x " or text[:3] == "-x ": text = "xfce4-terminal " + text
                    else:
                        text_class = self.path_subcom
                        if text[0] != "/": text = self.expand_path(text)
        return(text_class, text)

    def class_of_path(self, path):
        class_path = self.error_path_class
        file_ext = False
        if os.path.isfile(path):
            class_path = self.file_class
            root, ext = os.path.splitext(path)
            if ext == ".sublime-project": file_ext = self.sublime_project_file_ext
            if ext in [".mp4", ".webm", ".mkv", ".avi", ".jpg", ".png"]: file_ext = self.video_file_ext
            if ext in [".mp3"]: file_ext = self.music_file_ext
        elif os.path.isdir(path):
            class_path = self.dir_class
        return(class_path, file_ext)

    def tag_handler(self, exp):
        """ Обработчик тегов
        exp - тег или выражение (напр: tag1*tag2) без символов обозначения тега
        Возвращает: лист name_subcom
        """
        grep = " | ".join(["grep -F -i '{0}'".format(i) for i in exp.split("*")])
        # -i - убирает регистрозависимость
        cmd = "cat '{0}' | cut -f 1,3 | {1} | cut -f 1 | uniq".format(self.base_path, grep)
        out = subprocess.check_output(cmd, shell=True, universal_newlines=True).rstrip()
        return(out.split("\n"))

    def name_subcom_handler(self, text):
        """ Обработчик name_subcom
        text - текст name_subcom без символов обозначения
        Возвращает: лист строк на которые ссылается name_subcom
        """
        cmd = """cat '{0}' | grep -F "│{1}│" | cut -f 2""".format(self.base_path, text) # | sort
        out = subprocess.check_output(cmd, shell=True, universal_newlines=True).rstrip()
        return(out.split("\n"))

    def run_com_subcom(self, cmd):
        # xfce4-terminal
        # ~$ -H -x mpv https://youtu.be/aKl5DoX5alY│
        # ~$ -x mpv https://youtu.be/aKl5DoX5alY│
        # ~$ mpv https://youtu.be/aKl5DoX5alY│
        if cmd:
            subprocess.Popen(cmd, shell=True, cwd=self.home_dir)

#----
    def sha1sum_in_path_subcom(self, sha1sum):
        """
        Переводит sha1sum в лист найденных path_subcom
        """
        path_subcom_list = []
        cmd = "cut -f 2,4 '{0}' | grep -F '{1}' | cut -f 2".format(self.base_path, sha1sum)
        out = subprocess.check_output(cmd, shell=True, universal_newlines=True).rstrip()
        if out: path_subcom_list = out.split("\n")
        return(path_subcom_list)