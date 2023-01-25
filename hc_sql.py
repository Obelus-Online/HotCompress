import shutil
import uuid
import pymysql.cursors
import gzip
import os
from tempfile import gettempdir as tmp
from hashlib import sha256
from tabulate import tabulate as tb
import logging

import sql_scripts
import sql_scripts as ss
import hc_configure

conf = hc_configure.HotCompressConfiguration().get_db_config()

connection_string = {'host': conf['host'],
                     'user': conf['user'],
                     'password': conf['pass'],
                     'database': conf['name'],
                     'charset': 'utf8mb4',
                     'cursorclass': pymysql.cursors.DictCursor
                     }

log = logging.getLogger('HotCompress.sql_functions')


def set_temp_path(file_name):
    temp_path = os.path.normpath(tmp() + '/' + str(uuid.uuid4()))
    log.debug('CREATE TEMP PATH: {}'.format(temp_path))
    try:
        os.mkdir(temp_path)
    except BaseException as e:
        log.error('Could not write to temporary directory.')
        return None
    return os.path.normpath(temp_path + '/' + file_name)


def calculate_filesize(file_path):
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        return f.tell()


def get_basename(file_path):
    return os.path.basename(file_path)


def compute_hash(file_path):
    hasher = sha256()
    with open(file_path, 'rb') as f:
        #  Iterate over file 4096 bytes at a time until b"" (end of data) is reached.
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
            return hasher.hexdigest()


class HotCompressSql:
    connection_string = connection_string

    @staticmethod
    def __db_fetch_one(statement: str, *args):
        connection = pymysql.connect(**connection_string)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, *args)
        res = cursor.fetchone()
        if res is not None:
            return res
        else:
            res = {'idx': 0}
            return res

    @staticmethod
    def __db_fetch_all(statement: str, *args):
        connection = pymysql.connect(**connection_string)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, *args)
        return cursor.fetchall()

    @staticmethod
    def __db_insert_one(statement: str, *args):
        connection = pymysql.connect(**connection_string)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(statement, *args)
            connection.commit()

    @staticmethod
    def __db_delete_one(file_index):
        connection = pymysql.connect(**connection_string)
        args = file_index
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_scripts.delete_one_by_id, *args)
            connection.commit()

    def __init__(self):
        self.log = logging.getLogger('HotCompress.HotCompressSql.sql_functions')
        self.log.info('Initialize database connection.')
        connection = pymysql.connect(**self.connection_string)
        try:
            connection.connect()
            connection.close()
            self.log.info("Connection test succeeded!")
        except ConnectionError as e:
            self.log.error("Connection error occurred: {}".format(e))

    """
    Get a list of all files and return a table with the data.
    """
    def get_file_list(self):

        rows = self.__db_fetch_all(ss.get_file_list)
        return tb(rows, headers="keys")

    """
    Check if a file exists in the database, if it is found, display the database index.
    """
    def check_for_file(self, sha_sum):
        connection = pymysql.connect(**self.connection_string)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(ss.get_file_hash, sha_sum)
                res = cursor.fetchone()
                if res is None:
                    return 0
                else:
                    return res['idx']

    def check_for_file_by_id(self, file_index):
        connection = pymysql.connect(**self.connection_string)
        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT `idx` FROM data_meta WHERE `idx` = %s"
                cursor.execute(sql, file_index)
                res = cursor.fetchone()
                if res is None:
                    return 0
                else:
                    return res['idx']

    def delete_file_by_id(self, file_index):
        if self.check_for_file_by_id(file_index):
            self.log.info("Deleting file with id {}".format(file_index))
            self.__db_delete_one(file_index)
            return True
        else:
            self.log.info("Could not find file with ID: {}".format(file_index))
            return False

    def create_file_meta(self, file_name):
        log.info("Create file metadata for {}".format(file_name))
        base = get_basename(file_name)
        ext = os.path.splitext(base)[1]
        log.debug("BASE NAME: {}, EXTENSION: {}".format(base, ext))
        self.__db_insert_one(ss.insert_meta, (base, ext))

    def get_hash_by_file_id(self, file_index):
        sql = "SELECT `file_hash` FROM data_meta WHERE idx = %s"
        return self.__db_fetch_one(sql, file_index)['file_hash']

    def get_blob_count(self, file_index: int) -> int:
        connection = pymysql.connect(**self.connection_string)
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(ss.chunk_count, file_index)
                rows = cursor.fetchone()
                return int(rows['chunk_idx'])

    def get_file_name(self, file_index):
        sql = "SELECT file_name FROM data_meta WHERE idx = %s"
        return self.__db_fetch_one(sql, file_index)['file_name']

    def unpack_file(self, gz_file_path, file_name):
        self.log.info('Unpacking {}'.format(file_name))
        working_dir = os.path.normpath('./' + file_name)
        with open(working_dir, 'wb') as f_out:
            with gzip.open(gz_file_path, 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)
        return working_dir

    def read_blobs_to_file(self, file_index):
        file_name = self.get_file_name(file_index)
        tmp_path = set_temp_path(file_name) + ".gz.tmp"
        self.log.info('Writing to {}'.format(tmp_path))
        row_count = self.get_blob_count(file_index)
        self.log.info('Found file with {} rows. Beginning decompression.'.format(row_count))
        with open(tmp_path, 'wb') as tmp_file:
            for i in range(row_count):
                row = self.__db_fetch_one(ss.chunk_data, (file_index, i))
                # noinspection PyTypeChecker
                tmp_file.write(row['chunk_data'])
                self.log.info('Writing temporary chunk {}/{}'.format(i + 1, row_count))
            tmp_file.close()
            db_hash = self.get_hash_by_file_id(file_index)
            self.log.info('Database provided file hash: {}'.format(db_hash))
            self.log.info('Checking current file hash.')
            file_hash = compute_hash(self.unpack_file(tmp_path, file_name))
            self.log.info('Extracted hash: {}'.format(file_hash))
            if db_hash == file_hash:
                self.log.info('File hashes match!')
            else:
                self.log.warning('File hashes do not match')
            
    def write_blobs(self, file_path, chunk_size, file_index):
        tmp_path = set_temp_path(file_path) + ".gz.tmp"
        tmp_path = os.path.basename(tmp_path)
        with open(file_path, 'rb') as f_in:
            with gzip.open(tmp_path, 'wb', compresslevel=0) as f_out:
                shutil.copyfileobj(f_in, f_out)

        with open(tmp_path, 'rb') as tmp_file:
            full_size = calculate_filesize(file_path)
            sha_sum = compute_hash(file_path)
            self.check_for_file(sha_sum)
            size = calculate_filesize(tmp_path)
            chunks = size // chunk_size + 1

            i = 0
            while i < chunks:
                try:
                    data = tmp_file.read(chunk_size)
                    connection = pymysql.connect(**self.connection_string)
                    with connection:
                        with connection.cursor() as cursor:
                            sql = "INSERT INTO `data_chunks` (`file_idx`, `chunk_data`, `chunk_idx`)" \
                                  " VALUES(%s, %s, %s)"
                            cursor.execute(sql, (file_index, data, i))
                            connection.commit()
                    i += 1
                except pymysql.err.ProgrammingError as e:
                    log.debug("PYMYSQL ERROR")
                    exit(129)
                finally:
                    pass
            self.update_fileinfo(file_index, size, full_size, sha_sum, chunks)
        os.remove(tmp_path)

    def update_fileinfo(self, file_index, size, full_size, sha_sum, chunks):
        connection = pymysql.connect(**self.connection_string)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(ss.update_fileinfo, (full_size, size, chunks, sha_sum, file_index))
                connection.commit()
        return True

    def get_last_file_id(self):
        return self.__db_fetch_one(ss.next_file_id)['NEXT_ID']

    def get_latest_file_id(self):
        return self.__db_fetch_one(ss.last_file_id)['idx']

    def test_file_exists(self, file_path) -> int:
        """
        Check for the existence of a file hash in the database

                Parameters:
                        file_path (str): A filesystem path.

                Returns:
                        0 if hash not found, or the file index from the database.
        """
        log.info("Checking for file {}".format(file_path))
        file_hash = compute_hash(file_path)
        res = self.__db_fetch_one(ss.check_exists, file_hash)
        log.debug("RESULT SET: {}".format(res))
        if res['idx'] == 0:
            log.info("File {} not found in DB".format(file_path))
            return 0
        else:
            log.warning("File {} already exists in database, Id: {}".format(file_path, res['idx']))
            return res['idx']

