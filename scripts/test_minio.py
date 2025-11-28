import boto3
from botocore.exceptions import NoCredentialsError

# Konfiguracja połączenia z naszym lokalnym MinIO
s3 = boto3.client('s3',
    endpoint_url='http://localhost:9000', # Zwróć uwagę: port 9000 (API), a nie 9001 (Konsola)
    aws_access_key_id='admin',     # TU WPISZ SWÓJ LOGIN (z docker-compose)
    aws_secret_access_key='password123'  # TU WPISZ SWOJE HASŁO (z docker-compose)
)

bucket_name = 'devops-test-bucket'
file_name = 'test_plik.txt'
content = 'Witaj MinIO! To jest test z Pythona.'

def upload_to_minio():
    try:
        # 1. Najpierw tworzymy "kubełek" (bucket) na dane
        # W prawdziwym AWS S3 nazwy bucketów muszą być unikalne na świecie!
        print(f"Tworzę bucket: {bucket_name}...")
        s3.create_bucket(Bucket=bucket_name)

        # 2. Tworzymy przykładowy plik lokalnie
        with open(file_name, 'w') as f:
            f.write(content)

        # 3. Wysyłamy plik do MinIO
        print(f"Wysyłam plik {file_name}...")
        s3.upload_file(file_name, bucket_name, file_name)
        
        print("Sukces! ✅ Sprawdź w przeglądarce, czy plik się pojawił.")

    except Exception as e:
        print(f"Coś poszło nie tak: {e}")

if __name__ == '__main__':
    upload_to_minio()