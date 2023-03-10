#!/usr/bin/python3 test.py

import sys
import hc_sql
import re
import logging
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


def print_help():
    print("""
    Usage: hc.py [ FILE_1 FILE_2...] | DIRECTORY | ID_NUMBER
        
    Commands:
        print:          Display a list of items in the database.
        list:           Same as print
        delete ID_NUM:  Delete the file with the specified Id from the database. 
    """)


if __name__ == "__main__":
    log.info('Application start.')
    conf = hc_configure.HotCompressConfiguration().get_compression_config()
    db = hc_sql.HotCompressSql()
    if 'del' or 'DEL' or 'DELETE' or 'delete' in sys.argv:
        if re.search("^[0-9]+", sys.argv[2]):
            db.delete_file_by_id(sys.argv[2])
            exit(0)
        else:
            print_help()
            exit(0)



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
