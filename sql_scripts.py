get_file_list = "SELECT `idx`, `file_name`, `create_date`, `file_size`, `hash` FROM data_meta"

get_file_hash = "SELECT `idx` FROM data_meta WHERE `hash` = %s"

last_file_id = "SELECT idx FROM data_meta ORDER BY idx DESC LIMIT 1"

chunk_count = """
    SELECT COUNT(*) chunk_idx
    FROM 
        `data_chunks`
    WHERE 
        file_idx = %s;
"""

chunk_data = """
        SELECT chunk_data
        FROM 
            `data_chunks`
        WHERE 
            file_idx = %s
        AND
            chunk_idx = %s;
        """

update_fileinfo = """
        UPDATE `data_meta`
              SET
              `file_size` = %s,
              `file_size_compressed` = %s,
              `chunk_count` = %s,
              `hash` = %s
      WHERE
      idx = %s;
      """
