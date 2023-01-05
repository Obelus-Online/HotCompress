-- Dumping database structure for hot_compress
CREATE DATABASE IF NOT EXISTS `hot_compress` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `hot_compress`;

-- Dumping structure for table hot_compress.data_chunks
CREATE TABLE IF NOT EXISTS `data_chunks` (
  `idx` int(11) NOT NULL AUTO_INCREMENT,
  `chunk_idx` int(11) NOT NULL DEFAULT 0,
  `chunk_data` mediumblob NOT NULL,
  `file_idx` int(11) NOT NULL,
  PRIMARY KEY (`idx`),
  KEY `FK_data_chunks_data_metadata` (`file_idx`),
  CONSTRAINT `FK_data_chunks_data_metadata` FOREIGN KEY (`file_idx`) REFERENCES `data_meta` (`idx`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1064 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `data_meta` (
  `idx` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) NOT NULL DEFAULT 'file',
  `create_date` datetime DEFAULT current_timestamp(),
  `file_size` int(10) unsigned DEFAULT NULL,
  `file_size_compressed` int(10) unsigned DEFAULT NULL,
  `chunk_count` int(11) DEFAULT NULL,
  `extension` varchar(16) DEFAULT NULL,
  `file_hash` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`idx`)
) ENGINE=InnoDB AUTO_INCREMENT=211 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
