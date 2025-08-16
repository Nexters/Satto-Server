# src/storage_client/client.py
from __future__ import annotations

import threading
import uuid
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from src.common.logger import logger
from src.config.config import storage_config

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class ObjectStorageClient:
    _instance: "ObjectStorageClient | None" = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    self = super().__new__(cls)

                    self.bucket = storage_config.NCP_OS_BUCKET
                    # self.public_read = storage_config.NCP_OS_PUBLIC_READ

                    endpoint = storage_config.NCP_OS_ENDPOINT.rstrip("/")
                    self._endpoint = endpoint
                    self._host = urlparse(endpoint).netloc

                    # ✅ path-style + SigV4 강제
                    cfg = Config(
                        signature_version="s3v4",
                        s3={"addressing_style": "path"}
                    )

                    self._s3 = boto3.client(
                        "s3",
                        region_name=storage_config.NCP_OS_REGION,
                        endpoint_url=endpoint,
                        aws_access_key_id=storage_config.NCP_ACCESS_KEY,
                        aws_secret_access_key=storage_config.NCP_SECRET_KEY,
                        config=cfg,
                    )

                    def _safe(call, **kw):
                        try:
                            return call(**kw)
                        except Exception as e:
                            return f"ERROR: {e}"

                    logger.info("DEBUG_BUCKET start")
                    logger.info("location: %s", _safe(self._s3.get_bucket_location, Bucket=self.bucket))
                    logger.info("policy: %s", _safe(self._s3.get_bucket_policy, Bucket=self.bucket))
                    logger.info("policy_status: %s", _safe(self._s3.get_bucket_policy_status, Bucket=self.bucket))
                    logger.info("encryption: %s", _safe(self._s3.get_bucket_encryption, Bucket=self.bucket))
                    logger.info("public_access_block: %s", _safe(self._s3.get_public_access_block, Bucket=self.bucket))
                    logger.info("acl: %s", _safe(self._s3.get_bucket_acl, Bucket=self.bucket))
                    logger.info("DEBUG_BUCKET end")

                    logger.info(f"ObjectStorage connected: bucket={self.bucket}")
                    cls._instance = self
        return cls._instance

    def __init__(self) -> None:
        pass

    def make_key(self, *, prefix: str, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        return f"{prefix}/{uuid.uuid4().hex}{ext}"

    def upload_fileobj(self, fileobj, *, key: str, content_type: str | None = None) -> str:
        """
        파일을 업로드하고 최종 공개 URL(path-style)을 반환.
        우선 단일 PutObject로 최소 권한만 사용하여 테스트하고,
        필요시 multipart(upload_fileobj)로 바꿔도 됨.
        """
        logger.info(f"Uploading to bucket={self.bucket} key={key}")

        # ExtraArgs 구성 (버킷이 ACL 차단이면 public_read를 False로 두세요)
        extra: dict = {}
        if content_type:
            extra["ContentType"] = content_type
        # if self.public_read:
        #     # 버킷이 'ACL 차단(Object Ownership Enforced)'이면 이 줄이 AccessDenied 원인!
        #     extra["ACL"] = "public-read"

        try:
            # ✅ 최소 재현: PutObject (multipart 아님)
            #   UploadFile 같은 파일객체는 한번 읽으면 포인터가 이동하니, 항상 맨 앞으로
            try:
                fileobj.seek(0)
            except Exception:
                pass
            body = fileobj.read()
            self._s3.put_object(Bucket=self.bucket, Key=key, Body=body, **({k: v for k, v in extra.items() if k != "ACL"}))

            # ACL 허용 버킷일 때만 ACL 설정이 필요하면 별도 호출 (선택)
            if self.public_read:
                try:
                    self._s3.put_object_acl(Bucket=self.bucket, Key=key, ACL="public-read")
                except ClientError as e:
                    # ACL 차단 버킷이면 여기서 AccessDenied가 날 수 있음 → 무시하고 경고만
                    logger.warning(f"put_object_acl skipped: {e}")

        except ClientError as e:
            # 에러 디테일 로그
            code = e.response.get("Error", {}).get("Code")
            msg = e.response.get("Error", {}).get("Message")
            logger.error(f"PutObject failed: {code} - {msg}")
            # 힌트 포함해서 그대로 다시 던짐
            raise

        # ✅ 공개 URL은 path-style로 반환
        return f"https://{self._host}/{self.bucket}/{key}"

    def presigned_get(self, key: str, expires_in: int = 3600) -> str:
        return self._s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
