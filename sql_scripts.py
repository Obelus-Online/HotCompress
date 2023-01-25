get_file_list = "SELECT `idx`, `file_name`, `create_date`, `file_size`, `file_hash` FROM data_meta"

get_file_hash = "SELECT `idx` FROM data_meta WHERE `file_hash` = %s"

last_file_id = "SELECT idx FROM data_meta ORDER BY idx DESC LIMIT 1"

next_file_id = """
    SELECT
        AUTO_INCREMENT + 1 AS NEXT_ID
    FROM
        `information_schema`.`tables`
    WHERE
        TABLE_NAME = "data_meta";
    """


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
              `file_hash` = %s
      WHERE
      idx = %s;
      """

check_exists = """
        SELECT 
            idx, file_hash
        FROM 
            `data_meta`
        WHERE 
            file_hash = %s;
    """

delete_one_by_id = """
    DELETE FROM 
        data_meta
    WHERE
        idx=%s;
    """

insert_meta = """
        INSERT INTO 
            `data_meta` (`file_name`, `extension`)
        VALUES 
            (%s, %s);
    """
