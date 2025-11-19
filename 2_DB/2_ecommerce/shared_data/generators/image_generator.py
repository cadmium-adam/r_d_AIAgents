"""
Image generation functionality for product images.
Supports Stable Diffusion, Unsplash, and MinIO upload.
"""

import base64
import re
from typing import Dict, Any, Optional
from io import BytesIO

from minio import Minio

from diffusers import (
    SD3Transformer2DModel,
    BitsAndBytesConfig,
    StableDiffusion3Pipeline,
)
import torch


class ImageGenerator:
    """Handles all image generation and management functionality."""

    def __init__(
        self,
        minio_endpoint: str = "localhost:9000",
        minio_access_key: str = "admin",
        minio_secret_key: str = "password123",
    ):
        self.minio_client = None
        self.minio_bucket = "product-images"
        self.sd_pipeline = None

        # Initialize MinIO client
        try:
            self.minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False,
            )

            # Create bucket if it doesn't exist
            if not self.minio_client.bucket_exists(self.minio_bucket):
                self.minio_client.make_bucket(self.minio_bucket)
                print(f"✓ MinIO bucket '{self.minio_bucket}' created")
            else:
                print(f"✓ MinIO connected, using existing bucket '{self.minio_bucket}'")

        except Exception as e:
            print(
                f"⚠ Warning: Could not connect to MinIO ({e}). Images will not be uploaded."
            )
            self.minio_client = None

        # Initialize Stable Diffusion pipeline
        try:
            self._initialize_stable_diffusion()
        except Exception as e:
            print(
                f"⚠ Warning: Could not initialize Stable Diffusion ({e}). Using fallback images."
            )
            self.sd_pipeline = None

    def _initialize_stable_diffusion(self):
        """Initialize Stable Diffusion pipeline."""
        print("🤖 Initializing Stable Diffusion pipeline...")

        # model_id = "stabilityai/stable-diffusion-3.5-medium"
        model_id = "stabilityai/stable-diffusion-3.5-large"

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        model_4bit = SD3Transformer2DModel.from_pretrained(
            model_id,
            subfolder="transformer",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
        )

        self.sd_pipeline = StableDiffusion3Pipeline.from_pretrained(
            model_id, transformer=model_4bit, torch_dtype=torch.bfloat16
        )
        self.sd_pipeline.enable_model_cpu_offload()

        print("✓ Stable Diffusion pipeline initialized")

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing/replacing problematic characters."""
        # Replace spaces and common punctuation with underscores
        sanitized = re.sub(r"[,\s\-&\.\/\\\(\)\[\]{}]+", "_", filename)

        # Remove any remaining non-alphanumeric characters except underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "", sanitized)

        # Remove multiple consecutive underscores
        sanitized = re.sub(r"_+", "_", sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        # Ensure the filename isn't empty and isn't too long
        if not sanitized:
            sanitized = "product"

        # Limit length to avoid filesystem issues
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip("_")

        return sanitized

    def upload_image_to_minio(
        self, image_data: bytes, product_id: int, image_name: str
    ) -> Optional[str]:
        """Upload image to MinIO and return the URL."""
        if not self.minio_client:
            return None

        try:
            # Generate object name with proper folder structure
            object_name = f"products/{product_id}/{image_name}"

            # Upload image
            self.minio_client.put_object(
                self.minio_bucket,
                object_name,
                BytesIO(image_data),
                length=len(image_data),
                content_type=(
                    "image/png" if image_name.endswith(".png") else "image/jpeg"
                ),
            )

            # Return presigned MinIO URL (publicly accessible)
            from datetime import timedelta
            return self.minio_client.presigned_get_object(
                self.minio_bucket, 
                object_name, 
                expires=timedelta(days=7)  # URL valid for 7 days
            )

        except Exception as e:
            print(f"⚠ Failed to upload image to MinIO: {e}")
            return None

    def generate_stable_diffusion_image(
        self, product_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate product image using Stable Diffusion."""
        if not self.sd_pipeline:
            return None

        try:
            # Create concise prompt from product data (limit for CLIP 77-token constraint)
            name = product_data["name"]
            category = product_data["category"]

            # Create a short, focused prompt that stays within token limits
            prompt = f"{name}, {category} product, high quality, professional"

            # Generate image
            image = self.sd_pipeline(
                prompt=prompt,
                num_inference_steps=28,
                guidance_scale=4.5,
                max_sequence_length=512,
            ).images[0]

            # Convert to bytes
            img_buffer = BytesIO()
            image.save(img_buffer, format="PNG")
            image_data = img_buffer.getvalue()

            # Encode to base64
            b64_data = base64.b64encode(image_data).decode("utf-8")

            return {
                "base64": b64_data,
                "image_data": image_data,
                "url": None,  # Will be set if uploaded to MinIO
            }

        except Exception as e:
            print(
                f"⚠ Stable Diffusion image generation failed for {product_data.get('name', 'Unknown')}: {e}"
            )
            return None

    def generate_product_images(
        self,
        product_name: str,
        product_id: int,
        product_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate product image URLs based on category and product type."""

        # Generate with Stable Diffusion (always enabled)
        if product_data:
            sd_result = self.generate_stable_diffusion_image(product_data)
            if sd_result:
                # Upload Stable Diffusion image to MinIO
                if sd_result["image_data"]:
                    sanitized_name = self.sanitize_filename(product_name)
                    minio_url = self.upload_image_to_minio(
                        sd_result["image_data"], product_id, f"{sanitized_name}.png"
                    )
                    if minio_url:
                        sd_result["url"] = minio_url

                # Return Stable Diffusion generated image (URL only)
                if sd_result["url"]:
                    return {
                        "main_image": sd_result["url"],
                        "thumbnail": sd_result["url"],  # SD images are already appropriate size
                        "gallery": [sd_result["url"]],
                    }
                else:
                    # If MinIO upload failed, use placeholder
                    print(f"⚠ Warning: MinIO upload failed for {product_name}. Using placeholder.")
                    placeholder_url = f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300'><rect width='100%25' height='100%25' fill='%23ddd'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999'>Product Image</text></svg>"
                    return {
                        "main_image": placeholder_url,
                        "thumbnail": placeholder_url,
                        "gallery": [placeholder_url],
                    }

        # Fallback if Stable Diffusion fails - return placeholder
        print(
            f"⚠ Warning: Could not generate image for {product_name}. Using placeholder."
        )
        placeholder_url = f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='300'><rect width='100%25' height='100%25' fill='%23ddd'/><text x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999'>Product Image</text></svg>"

        return {
            "main_image": placeholder_url,
            "thumbnail": placeholder_url,
            "gallery": [placeholder_url],
        }
