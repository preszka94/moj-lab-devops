SET LINESIZE 200;
COLUMN uuid FORMAT A38;
COLUMN seller_name FORMAT A40;
COLUMN total_amount FORMAT 99999.99;
COLUMN status FORMAT A18;

SELECT uuid, seller_name, total_amount, status FROM invoice_metadata;
EXIT;