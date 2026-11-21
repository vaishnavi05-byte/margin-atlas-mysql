CREATE DATABASE IF NOT EXISTS margin_atlas
CHARACTER SET utf8mb4;

USE margin_atlas;

SELECT VERSION() AS mysql_version,
       DATABASE() AS current_database;