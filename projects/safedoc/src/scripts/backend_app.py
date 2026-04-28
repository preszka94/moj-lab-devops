import os
import sys
import uuid
import boto3
import oracledb
from google.cloud import documentai
from google.api_core.client_options import ClientOptions

# --- CONFIGURATION: GCP Document AI ---
# Tell Python where our service account JSON key is located
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "scripts/gcp-credentials.json"
PROJECT_ID = "safedoc-flow" # Your GCP Project ID
LOCATION = "eu" # or "us" - depending on where you created the processor
PROCESSOR_ID = "c7b215ed4781b80" # <--- PASTE YOUR ID HERE

# --- CONFIGURATION: MinIO ---
MINIO_ENDPOINT = 'http://localhost:9000'
ACCESS_KEY = 'admin'
SECRET_KEY = 'password123'
BUCKET_NAME = 'safedoc-invoices'

# --- CONFIGURATION: Oracle DB ---
DB_USER = "system"
DB_PASSWORD = "admin123"
DB_DSN = "localhost:1521/FREEPDB1"

# Initialize MinIO client
s3_client = boto3.client('s3', endpoint_url=MINIO_ENDPOINT, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

def extract_data_with_gcp(file_path):
    print("🧠 [Document AI] Sending document to Google Cloud...")
    
# NEW FIX: Explicitly tell the client to use the European endpoint
    if LOCATION == "eu":
        client_options = ClientOptions(api_endpoint="eu-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=client_options)
    else:
        client = documentai.DocumentProcessorServiceClient()
        
    name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    # Read the file from disk
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Auto-detect file type
    mime_type = "application/pdf" if file_path.lower().endswith(".pdf") else "image/jpeg"
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    # Send the request to Google API
    result = client.process_document(request=request)
    document = result.document

    # Prepare an empty dictionary with default values
    invoice_data = {
        "seller_name": "Not found",
        "buyer_name": "Not found",
        "nip": "Not found",
        "purchase_month": "Not found",
        "total_amount": 0.0,
        "vat_percentage": 0.0
    }

    print("🔍 [Document AI] Document analyzed. Extracting values...")
    
    # Google Document AI Magic: Loop through all extracted "entities"
    for entity in document.entities:
        type_ = entity.type_
        value = entity.mention_text.strip()
        
        if type_ == "supplier_name":
            invoice_data["seller_name"] = value
        elif type_ == "receiver_name":
            invoice_data["buyer_name"] = value
        elif type_ == "supplier_tax_id":
            invoice_data["nip"] = value
        elif type_ == "invoice_date":
            invoice_data["purchase_month"] = value
        elif type_ == "total_amount":
            try:
                # Clean the amount from currency and spaces so it fits into an Oracle FLOAT/NUMBER
                clean_value = value.replace(',', '.').replace(' ', '').replace('PLN', '').replace('zł', '')
                invoice_data["total_amount"] = float(clean_value)
            except ValueError:
                pass
        elif type_ == "total_tax_amount":
            try:
                clean_value = value.replace(',', '.').replace(' ', '').replace('PLN', '').replace('zł', '')
                invoice_data["vat_percentage"] = float(clean_value)
            except ValueError:
                pass

    return invoice_data

def process_invoice(file_path):
    print(f"\n{'='*50}\n📥 Processing file: {os.path.basename(file_path)}")

    # 1. Validation
    valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() not in valid_extensions:
        print("❌ Error: Unsupported document format. Rejecting file.")
        # Return to bash instead of sys.exit(1) to avoid breaking the loop for the next files!
        return 

    # 2. Generate UUID
    invoice_uuid = str(uuid.uuid4())
    object_name = f"{invoice_uuid}{file_extension.lower()}"
    print(f"🔑 Assigned UUID: {invoice_uuid}")

    # 3. Save to MinIO
    try:
        try:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            pass 
        s3_client.upload_file(file_path, BUCKET_NAME, object_name)
        print(f"☁️ MinIO: File archived as {object_name}")
    except Exception as e:
        print(f"🔥 MinIO Error: {e}")
        return

    # 4. AI Extraction
    try:
        ai_data = extract_data_with_gcp(file_path)
        print(f"📊 EXTRACTED DATA: Seller: {ai_data['seller_name']}, NIP: {ai_data['nip']}, Amount: {ai_data['total_amount']}")
    except Exception as e:
        print(f"🔥 AI Error: {e}")
        return

    # 5. Save to Oracle DB
    try:
        connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = connection.cursor()
        
        insert_sql = """
        INSERT INTO invoice_metadata 
        (uuid, filename, status, seller_name, buyer_name, nip, purchase_month, total_amount, vat_percentage) 
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
        """
        
        cursor.execute(insert_sql, [
            invoice_uuid, object_name, "GCP_AI_PROCESSED", 
            ai_data['seller_name'], ai_data['buyer_name'], ai_data['nip'], 
            ai_data['purchase_month'], ai_data['total_amount'], ai_data['vat_percentage']
        ])
        
        connection.commit()
        print("💾 Oracle DB: Saved successfully!")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"🔥 Database Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 backend_app.py <file_path>")
        sys.exit(1)
        
    process_invoice(sys.argv[1])