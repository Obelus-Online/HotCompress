#!/usr/bin/python3 test.py

import sys
import sql_functions
import re
import logging
import hc_configure

log = logging.getLogger('HotCompress')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logstream = logging.StreamHandler()
logstream.setLevel(logging.DEBUG)
logstream.setFormatter(formatter)

log.addHandler(logstream)

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
        elif x is not None:
            log.debug('GETTING LAST FILE ID')
            if db.check_for_file_by_id(arg):
                print('found!')
            else:
                print('no bueno!')
            exit(2)
        else:
            db.create_file(arg)
            file_index = db.get_last_file_id()
            db.write_blobs(arg, conf['chunk_size'], file_index)
