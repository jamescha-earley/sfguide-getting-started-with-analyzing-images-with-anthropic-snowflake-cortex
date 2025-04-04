CREATE DATABASE IF NOT EXISTS image_analysis;
CREATE SCHEMA IF NOT EXISTS image_analysis;

-- Create Image Storage Stage
CREATE STAGE IF NOT EXISTS image_analysis.images
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  DIRECTORY = (ENABLE = true);

-- Verify upload success 
-- ls @image_analysis.images;

-- Create Image Processing Tables
-- Create an image table that references the files in our stage
CREATE OR REPLACE TABLE image_analysis.image_table AS
  SELECT 
    RELATIVE_PATH AS image_path,
    TO_FILE('@image_analysis.images', RELATIVE_PATH) AS img_file
  FROM DIRECTORY('@image_analysis.images');