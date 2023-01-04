import os
import pathlib
import logging

log = logging.getLogger('HotCompress.hc_filehandling')


class HcFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def check_folder(self):
        return os.path.isdir(self.file_path)

    def get_file_list(self):
        file_list = []
        dir_list = os.listdir(self.file_path)
        for file in dir_list:
            path = os.path.normpath(self.file_path + '/' + file)
            if os.path.isfile(path):
                file_list.append(path)
        return file_list
