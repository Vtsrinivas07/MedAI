import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid
from datetime import datetime

from config.settings import settings

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET
    
    async def upload_medical_report(
        self,
        file_data: bytes,
        user_id: str,
        file_name: str,
        content_type: str
    ) -> dict:
        """Upload medical report or image to S3"""
        try:
            # Generate unique file key
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_extension = file_name.split('.')[-1] if '.' in file_name else 'pdf'
            s3_key = f"medical_reports/{user_id}/{timestamp}_{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'user_id': user_id,
                    'original_filename': file_name,
                    'upload_date': timestamp
                }
            )
            
            # Generate presigned URL for access (valid for 7 days)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=604800  # 7 days
            )
            
            return {
                "success": True,
                "file_key": s3_key,
                "url": url,
                "bucket": self.bucket_name,
                "message": "File uploaded successfully"
            }
        
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to upload file"
            }
    
    async def get_medical_report(self, file_key: str) -> Optional[bytes]:
        """Download medical report from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response['Body'].read()
        
        except ClientError as e:
            print(f"Error downloading file: {str(e)}")
            return None
    
    async def delete_medical_report(self, file_key: str) -> bool:
        """Delete medical report from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        
        except ClientError as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    async def list_user_reports(self, user_id: str) -> list:
        """List all medical reports for a user"""
        try:
            prefix = f"medical_reports/{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            reports = []
            for obj in response.get('Contents', []):
                # Get metadata
                metadata = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                
                # Generate presigned URL
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': obj['Key']
                    },
                    ExpiresIn=604800  # 7 days
                )
                
                reports.append({
                    "file_key": obj['Key'],
                    "file_name": metadata.get('Metadata', {}).get('original_filename', 'Unknown'),
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "url": url
                })
            
            return reports
        
        except ClientError as e:
            print(f"Error listing files: {str(e)}")
            return []
