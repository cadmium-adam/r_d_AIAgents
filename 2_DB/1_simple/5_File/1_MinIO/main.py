#!/usr/bin/env python3
"""
MinIO Demonstration Script
Shows how to perform various operations with MinIO including:
- Bucket operations (create, list, remove)
- File operations (upload with MIME types, download, rename, delete)
- URL generation
- Working with folder structures
"""

import os
import sys
from datetime import timedelta
from pathlib import Path
from typing import Optional, List, Tuple

import magic
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource


class MinIODemo:
    def __init__(
        self, endpoint: str, access_key: str, secret_key: str, secure: bool = False
    ):
        """Initialize MinIO client."""
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.mime = magic.Magic(mime=True)

    def create_bucket(self, bucket_name: str) -> bool:
        """Create a new bucket."""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"✓ Bucket '{bucket_name}' created successfully")
                return True
            else:
                print(f"! Bucket '{bucket_name}' already exists")
                return False
        except S3Error as e:
            print(f"✗ Error creating bucket: {e}")
            return False

    def list_buckets(self) -> List[str]:
        """List all buckets."""
        try:
            buckets = self.client.list_buckets()
            print("\n📦 Available buckets:")
            bucket_names = []
            for bucket in buckets:
                print(f"  - {bucket.name} (created: {bucket.creation_date})")
                bucket_names.append(bucket.name)
            return bucket_names
        except S3Error as e:
            print(f"✗ Error listing buckets: {e}")
            return []

    def remove_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """Remove a bucket (must be empty unless force=True)."""
        try:
            if force:
                # Remove all objects first
                objects = self.client.list_objects(bucket_name, recursive=True)
                for obj in objects:
                    self.client.remove_object(bucket_name, obj.object_name)
                    print(f"  - Removed object: {obj.object_name}")

            self.client.remove_bucket(bucket_name)
            print(f"✓ Bucket '{bucket_name}' removed successfully")
            return True
        except S3Error as e:
            print(f"✗ Error removing bucket: {e}")
            return False

    def upload_file(
        self, bucket_name: str, file_path: Path, object_name: Optional[str] = None
    ) -> bool:
        """Upload a file with automatic MIME type detection."""
        try:
            if object_name is None:
                object_name = file_path.name

            # Detect MIME type
            mime_type = self.mime.from_file(str(file_path))

            # Upload file
            self.client.fput_object(
                bucket_name, object_name, str(file_path), content_type=mime_type
            )
            print(f"✓ Uploaded '{file_path}' as '{object_name}' (MIME: {mime_type})")
            return True
        except S3Error as e:
            print(f"✗ Error uploading file: {e}")
            return False

    def upload_folder(
        self, bucket_name: str, folder_path: Path, preserve_structure: bool = True
    ) -> List[Tuple[Path, str]]:
        """Upload all files from a folder, optionally preserving folder structure."""
        uploaded = []

        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                if preserve_structure:
                    # Preserve relative path structure
                    object_name = str(file_path.relative_to(folder_path.parent))
                else:
                    # Flatten structure
                    object_name = file_path.name

                if self.upload_file(bucket_name, file_path, object_name):
                    uploaded.append((file_path, object_name))

        return uploaded

    def download_file(
        self, bucket_name: str, object_name: str, file_path: Path
    ) -> bool:
        """Download a file from MinIO."""
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            self.client.fget_object(bucket_name, object_name, str(file_path))
            print(f"✓ Downloaded '{object_name}' to '{file_path}'")
            return True
        except S3Error as e:
            print(f"✗ Error downloading file: {e}")
            return False

    def rename_file(self, bucket_name: str, old_name: str, new_name: str) -> bool:
        """Rename a file (copy then delete)."""
        try:
            # Copy object to new name
            copy_source = CopySource(bucket_name, old_name)
            self.client.copy_object(bucket_name, new_name, copy_source)

            # Delete old object
            self.client.remove_object(bucket_name, old_name)
            print(f"✓ Renamed '{old_name}' to '{new_name}'")
            return True
        except S3Error as e:
            print(f"✗ Error renaming file: {e}")
            return False

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """Delete a file from MinIO."""
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"✓ Deleted '{object_name}'")
            return True
        except S3Error as e:
            print(f"✗ Error deleting file: {e}")
            return False

    def list_files(
        self, bucket_name: str, prefix: str = "", recursive: bool = True
    ) -> List[str]:
        """List all files in a bucket."""
        try:
            objects = self.client.list_objects(
                bucket_name, prefix=prefix, recursive=recursive
            )
            print(f"\n📁 Files in bucket '{bucket_name}':")
            file_names = []
            for obj in objects:
                print(
                    f"  - {obj.object_name} ({obj.size} bytes, modified: {obj.last_modified})"
                )
                file_names.append(obj.object_name)
            return file_names
        except S3Error as e:
            print(f"✗ Error listing files: {e}")
            return []

    def get_file_url(
        self, bucket_name: str, object_name: str, expiry_days: int = 7
    ) -> Optional[str]:
        """Generate a presigned URL for file access."""
        try:
            url = self.client.presigned_get_object(
                bucket_name, object_name, expires=timedelta(days=expiry_days)
            )
            print(
                f"✓ Generated URL for '{object_name}' (expires in {expiry_days} days):"
            )
            print(f"  {url}")
            return url
        except S3Error as e:
            print(f"✗ Error generating URL: {e}")
            return None


def main():
    """Demonstrate MinIO operations."""
    # MinIO connection settings (adjust these for your MinIO instance)
    MINIO_ENDPOINT = "localhost:9000"  # or "minio.example.com"
    MINIO_ACCESS_KEY = "admin"  # change to your access key
    MINIO_SECRET_KEY = "password123"  # change to your secret key
    MINIO_SECURE = False  # set to True for HTTPS

    # Initialize MinIO client
    print("🚀 MinIO Demonstration Script")
    print("=" * 50)

    demo = MinIODemo(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE)

    # Demo bucket name
    bucket_name = "demo-bucket"

    # 1. Create bucket
    print("\n1️⃣ Creating bucket...")
    demo.create_bucket(bucket_name)

    # 2. List buckets
    print("\n2️⃣ Listing buckets...")
    demo.list_buckets()

    # 3. Upload files from 'files' folder
    print("\n3️⃣ Uploading files from 'files' folder...")
    files_folder = Path("files")
    if files_folder.exists():
        uploaded_files = demo.upload_folder(
            bucket_name, files_folder, preserve_structure=True
        )
        print(f"  Uploaded {len(uploaded_files)} files")

    # 4. List files in bucket
    print("\n4️⃣ Listing files in bucket...")
    demo.list_files(bucket_name)

    # 5. Rename a file
    if uploaded_files:
        print("\n5️⃣ Renaming a file...")
        old_name = uploaded_files[0][1]
        new_name = f"renamed_{Path(old_name).name}"
        demo.rename_file(bucket_name, old_name, new_name)

    # 6. Download a file
    print("\n6️⃣ Downloading a file...")
    download_folder = Path("downloads")
    download_folder.mkdir(exist_ok=True)
    if uploaded_files and len(uploaded_files) > 1:
        object_to_download = uploaded_files[1][1]
        demo.download_file(
            bucket_name,
            object_to_download,
            download_folder / Path(object_to_download).name,
        )

    # 7. Generate presigned URL
    print("\n7️⃣ Generating presigned URL...")
    if uploaded_files:
        demo.get_file_url(
            bucket_name, new_name if "new_name" in locals() else uploaded_files[0][1]
        )

    # 8. Delete a file
    print("\n8️⃣ Deleting a file...")
    if "new_name" in locals():
        demo.delete_file(bucket_name, new_name)

    # 9. Remove bucket (optional - commented out to preserve data)
    print("\n9️⃣ Bucket removal (skipped to preserve data)")
    # demo.remove_bucket(bucket_name, force=True)

    print("\n✅ Demo completed!")
    print(
        "\nTo remove the bucket and all its contents, uncomment the last line in main()"
    )


if __name__ == "__main__":
    main()
