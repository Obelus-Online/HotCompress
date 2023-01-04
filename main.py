#!/usr/bin/python3 test.py

import sys
import sql_functions
import re
import logging
import os
import hc_configure
import hc_filehandling

log = logging.getLogger('HotCompress')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
logstream.setFormatter(formatter)

log.addHandler(logstream)


def add_file_to_db(file_path):
    log.debug("TEST PATH".format(db.test_file_exists(file_path)))
    if db.test_file_exists(file_path) == 0:
        db.create_file_meta(file_path)
        file_index = db.get_latest_file_id()
        print(file_index)
        db.write_blobs(file_path, conf['chunk_size'], file_index)
    else:
        pass


if __name__ == "__main__":
    log.info('Application start.')
    conf = hc_configure.HotCompressConfiguration().get_compression_config()

    db = sql_functions.HotCompressSql()
    for i, arg in enumerate(sys.argv[1:]):

        x = re.search("^[0-9]", arg)
        if x is not None:
            log.info('Searching for file with index {}'.format(arg))
            if db.check_for_file_by_id(arg):
                log.info('Found file with index {}'.format(arg))
                db.read_blobs_to_file(arg)
                exit(0)
            else:
                log.info('Could not find file with index {}. Exiting, buh-bye.'.format(arg))
                exit(129)

        if arg in ["print", "PRINT", "list", "list"]:
            print(db.get_file_list())
            exit(0)
        else:
            fh = hc_filehandling.HcFileHandler(arg)
            if fh.check_folder():
                file_list = fh.get_file_list()
                for file in file_list:
                    log.debug("FILE CONTENT {}".format(file))
                    log.info("Found file: {}".format(file))
                    add_file_to_db(file)

            else:
                add_file_to_db(arg)
