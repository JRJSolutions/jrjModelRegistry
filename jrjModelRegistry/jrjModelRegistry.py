import dill as pickle
import boto3
import os
from pathlib import Path

import os
import dill as pickle
import boto3
import requests
from pathlib import Path
from jrjModelRegistry.mongo import new_model
from . import jrjModelRegistryConfig
import pyzipper
from functools import partial

import os
import dill
from dill.detect import trace

from dill.detect import baditems

import copy
import dill
import types

import gc

import logging
import sys


import os
import zstandard as zstd
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC_HEADER = b"JRJ1"  # simple format/version marker


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 256-bit key
        salt=salt,
        iterations=200_000,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_with_password(plaintext: bytes, password: str) -> bytes:
    """
    Format: MAGIC (4) | SALT (16) | NONCE (12) | CIPHERTEXT+TAG
    """
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return MAGIC_HEADER + salt + nonce + ciphertext


def decrypt_with_password(blob: bytes, password: str) -> bytes:
    """
    Reverse of encrypt_with_password.
    Expects: MAGIC (4) | SALT (16) | NONCE (12) | CIPHERTEXT+TAG
    """
    if not blob.startswith(MAGIC_HEADER):
        raise ValueError("Invalid encrypted blob header")

    offset = len(MAGIC_HEADER)
    salt = blob[offset:offset + 16]
    nonce = blob[offset + 16:offset + 16 + 12]
    ciphertext = blob[offset + 16 + 12:]

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



from .mongo import delete_model, search_models_common



async def transformer(test):
    return test
def mainPredictor(x):
    return x


def is_dillable(obj):
    try:
        dill.dumps(obj, recurse=True)
        return True
    except Exception:
        return False

def clean_non_dillable_attributes(obj):
    obj_copy = copy.deepcopy(obj)
    # for attr in dir(obj_copy):
    #     if attr.startswith("__") and attr.endswith("__"):
    #         continue
    #     try:
    #         value = getattr(obj_copy, attr)
    #         if not is_dillable(value):
    #             setattr(obj_copy, attr, None)
    #     except Exception:
    #         setattr(obj_copy, attr, None)
    return obj_copy


def registerAJrjModel(model, config):
    modelName = config.get('modelName')
    version = config.get('version')
    modelFileType = config.get('modelFileType', 'pkl')
    modelType = config.get('modelType', 'model')
    config['modelType'] = modelType
    keepLastOnly = config.get('keepLastOnly', False)
    config['keepLastOnly'] = keepLastOnly

    if not modelName or not version:
        raise ValueError("`modelName` and `version` are required in the config.")

    if hasattr(model, "transformer"):
        model.transformer = partial(model.transformer)
    else:
        model.transformer = partial(transformer)

    if hasattr(model, "mainPredictor"):
        model.mainPredictor = partial(model.mainPredictor)
    else:
        model.mainPredictor = partial(mainPredictor)

    issues = baditems(model)
    if issues:
        for name, problem in issues.items():
            print(f"❌  baditems {name}: {problem}")

    filename = f"{modelName}__{version}.{modelFileType}"
    zip_filename = f"{filename}.zip"   # used in legacy path

    # Prepare paths
    local_dir = Path.cwd() / ".~jrjModelRegistry"
    local_dir.mkdir(parents=True, exist_ok=True)
    model_path = local_dir / filename

    clean_copy = clean_non_dillable_attributes(model)

    # Serialize model
    with open(model_path, "wb") as f:
        pickle.dump(clean_copy, f)
    config['modelSizeBytes'] = model_path.stat().st_size

    # Get password from env
    zip_password = jrjModelRegistryConfig.get("zipPassword")
    if not zip_password:
        raise EnvironmentError("zipPassword is not set")

    # Decide compression type
    compress_type = config.get("zompressType")  # NOTE: using *your* key name

    # ---------------------------------------------------------------------
    # NEW PATH: zstd + AES-GCM file encryption when zompressType == "zstd"
    # ---------------------------------------------------------------------
    if compress_type == "zstd":
        zst_filename = f"{filename}.zst"
        enc_filename = f"{zst_filename}.enc"

        zst_path = local_dir / zst_filename
        enc_path = local_dir / enc_filename

        # zstd compress (streaming)
        print("🧩 Compressing model with zstd...")
        cctx = zstd.ZstdCompressor(level=10, threads=-1)
        with open(model_path, "rb") as src, open(zst_path, "wb") as dst:
            with cctx.stream_writer(dst) as compressor:
                while True:
                    chunk = src.read(1024 * 1024)  # 1 MB
                    if not chunk:
                        break
                    compressor.write(chunk)

        config["compressedModelSizeBytes"] = zst_path.stat().st_size

        # Encrypt compressed bytes with same password
        print("🔐 Encrypting compressed model (AES-GCM + password)...")
        with open(zst_path, "rb") as f:
            compressed_data = f.read()
        encrypted_blob = encrypt_with_password(compressed_data, zip_password)

        with open(enc_path, "wb") as f:
            f.write(encrypted_blob)

        config["encryptedModelSizeBytes"] = enc_path.stat().st_size
        # For backward compatibility if anything expects this key name:
        config["zippedModelSizeBytes"] = config["encryptedModelSizeBytes"]

        # Upload to S3 using pre-signed URL
        s3 = boto3.client(
            "s3",
            endpoint_url=f'https://{jrjModelRegistryConfig.get("s3Endpoint")}',
            region_name=jrjModelRegistryConfig.get('s3Region'),
            aws_access_key_id=jrjModelRegistryConfig.get('s3KeyId'),
            aws_secret_access_key=jrjModelRegistryConfig.get('s3KeySecret'),
        )

        bucket_name = jrjModelRegistryConfig.get('s3BucketName')
        s3_key = enc_filename

        try:
            presigned_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': bucket_name, 'Key': s3_key},
                ExpiresIn=600,
                HttpMethod='PUT'
            )

            with open(enc_path, 'rb') as f:
                response = requests.put(presigned_url, data=f)

            if response.status_code == 200:
                print(f"✅ Uploaded encrypted ZSTD model to s3://{bucket_name}/{s3_key}")
                config['s3Url'] = f"{bucket_name}/{s3_key}"
                res = new_model(config)

                if keepLastOnly:
                    search_model_result = search_models_common({
                        "search": {
                            "orderBy": [{"createdAt": "desc"}],
                            "where": {
                                "modelName": modelName,
                                "version": {"$nin": [version]},
                            },
                            "pagination": {"page": 1, "size": 100000},
                        }
                    })
                    if search_model_result['count'] > 0:
                        for mm in search_model_result['data']:
                            s3Url = mm.get('s3Url')
                            _id = str(mm.get('_id'))
                            print(f"deleting model {_id} with s3Url {s3Url}")
                            if s3Url:
                                deleteAJrjModelAsset(s3Url)
                            delete_model(_id)

                return res
            else:  # pragma: no cover
                print(f"❌ Upload failed via PUT: {response.status_code} {response.text}")
                return None

        except Exception as e:  # pragma: no cover
            print(f"❌ Failed to generate URL or upload: {e}")
            return None

        finally:
            for p in [model_path, zst_path, enc_path]:
                try:
                    p.unlink()
                except Exception as cleanup_err:  # pragma: no cover
                    print(f"⚠️ Failed to delete {p}: {cleanup_err}")

    # ---------------------------------------------------------------------
    # LEGACY PATH: keep your original ZIP + pyzipper behavior as-is
    # ---------------------------------------------------------------------
    else:
        zip_path = local_dir / zip_filename

        # Create password-protected ZIP (unchanged)
        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA) as zipf:
            zipf.setpassword(zip_password.encode())
            zipf.setencryption(pyzipper.WZ_AES, nbits=256)
            zipf.write(model_path, arcname=filename)

        config['zippedModelSizeBytes'] = zip_path.stat().st_size

        # Upload to S3 using pre-signed URL (UNCHANGED BLOCK)
        s3 = boto3.client(
            "s3",
            endpoint_url=f'https://{jrjModelRegistryConfig.get("s3Endpoint")}',
            region_name=jrjModelRegistryConfig.get('s3Region'),
            aws_access_key_id=jrjModelRegistryConfig.get('s3KeyId'),
            aws_secret_access_key=jrjModelRegistryConfig.get('s3KeySecret'),
        )

        bucket_name = jrjModelRegistryConfig.get('s3BucketName')

        try:
            presigned_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={'Bucket': bucket_name, 'Key': zip_filename},
                ExpiresIn=600,
                HttpMethod='PUT'
            )

            with open(zip_path, 'rb') as f:
                response = requests.put(presigned_url, data=f)

            if response.status_code == 200:
                print(f"✅ Uploaded encrypted ZIP to s3://{bucket_name}/{zip_filename}")
                config['s3Url'] = f"{bucket_name}/{zip_filename}"
                res = new_model(config)

                if keepLastOnly:
                    search_model_result = search_models_common({
                        "search": {
                            "orderBy": [
                                {"createdAt": "desc"}
                            ],
                            "where": {
                                "modelName": modelName,
                                "version": {
                                    "$nin": [version]
                                }
                            },
                            "pagination": {
                                "page": 1,
                                "size": 100000
                            }
                        }
                    })
                    if search_model_result['count'] > 0:
                        for mm in search_model_result['data']:
                            s3Url = mm.get('s3Url')
                            _id = str(mm.get('_id'))
                            print(f"deleting model {_id} with s3Url {s3Url}")
                            if s3Url:
                                deleteAJrjModelAsset(s3Url)
                            delete_model(_id)
                return res
            else:  # pragma: no cover
                print(f"❌ Upload failed via PUT: {response.status_code} {response.text}")
                return None

        except Exception as e:  # pragma: no cover
            print(f"❌ Failed to generate URL or upload: {e}")
            return None

        finally:
            for p in [model_path, zip_path]:
                try:
                    p.unlink()
                except Exception as cleanup_err:  # pragma: no cover
                    print(f"⚠️ Failed to delete {p}: {cleanup_err}")



def deleteAJrjModelAsset(s3AssetPath):
    """
    Deletes a model asset from S3 using the given s3AssetPath (e.g., 'my-bucket/my-model__v1.pkl.zip')
    """
    try:
        bucket_name, key = s3AssetPath.split('/', 1)

        s3 = boto3.client(
            "s3",
            endpoint_url = f'https://{jrjModelRegistryConfig.get("s3Endpoint")}',
            region_name=jrjModelRegistryConfig.get('s3Region'),
            aws_access_key_id=jrjModelRegistryConfig.get('s3KeyId'),
            aws_secret_access_key=jrjModelRegistryConfig.get('s3KeySecret'),
        )

        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"🗑️ Deleted s3://{bucket_name}/{key}")
        return True

    except Exception as e:
        print(f"❌ Failed to delete S3 asset '{s3AssetPath}': {e}")
        return False




def loadAJrjModel(modelObj, max_retries=4):
    logging.info(
        f"Loading model {modelObj.get('modelName', 'modelName')} "
        f"version {modelObj.get('version', 'version')}"
    )

    s3_url = modelObj.get("s3Url")
    if not s3_url or "/" not in s3_url:  # pragma: no cover
        raise ValueError("Invalid or missing `s3Url` in modelObj")

    bucket_name, key = s3_url.split("/", 1)

    zip_password = jrjModelRegistryConfig.get("zipPassword")
    if not zip_password:  # pragma: no cover
        raise EnvironmentError("zipPassword is not set")

    local_dir = Path.cwd() / ".~jrjModelRegistry"
    local_dir.mkdir(parents=True, exist_ok=True)

    remote_filename = Path(key).name

    print(remote_filename)

    # Decide compression/encryption type based on file extension
    if remote_filename.endswith(".zip"):
        compression_mode = "zip"
        model_filename = remote_filename.replace(".zip", "")
    elif ".zst" in remote_filename:
        compression_mode = "zstd"
        # support both *.zst and *.zst.enc
        if remote_filename.endswith(".zst.enc"):
            model_filename = remote_filename[: -len(".zst.enc")]
        elif remote_filename.endswith(".zst"):
            model_filename = remote_filename[: -len(".zst")]
        else:
            # fallback if something weird like *.pkl.zst.something
            idx = remote_filename.rfind(".zst")
            model_filename = remote_filename[:idx]
    else:
        raise ValueError(
            f"Unknown model file type for key '{remote_filename}'. "
            f"Expected .zip or .zst/.zst.enc"
        )

    local_remote_path = local_dir / remote_filename   # .zip or .zst(.enc)
    local_model_path = local_dir / model_filename     # uncompressed pickle

    # If already extracted, try loading from local cache
    if local_model_path.exists():
        try:
            with open(local_model_path, "rb") as f:
                gc.collect()
                return pickle.load(f)
        except Exception as e:  # pragma: no cover
            print(f"⚠️ Failed to load cached model. Redownloading... ({e})")

    # Setup S3 client
    s3 = boto3.client(
        "s3",
        endpoint_url=f'https://{jrjModelRegistryConfig.get("s3Endpoint")}',
        region_name=jrjModelRegistryConfig.get('s3Region'),
        aws_access_key_id=jrjModelRegistryConfig.get('s3KeyId'),
        aws_secret_access_key=jrjModelRegistryConfig.get('s3KeySecret'),
    )

    for attempt in range(1, max_retries + 1):
        try:
            # Download remote file (.zip or .zst/.zst.enc)
            if not local_remote_path.exists() or attempt > 1:
                if local_remote_path.exists():
                    local_remote_path.unlink()  # Remove old file
                with open(local_remote_path, "wb") as f:
                    s3.download_fileobj(bucket_name, key, f)

            # ---------------- ZIP PATH (legacy, unchanged behavior) ----------------
            if compression_mode == "zip":
                with pyzipper.AESZipFile(local_remote_path, 'r') as zf:
                    zf.setpassword(zip_password.encode())
                    with open(local_model_path, "wb") as out_file:
                        out_file.write(zf.read(model_filename))

            # ---------------- ZSTD + AES PATH (new) ----------------
            else:  # compression_mode == "zstd"
                # 1) Read encrypted+compressed blob
                with open(local_remote_path, "rb") as f:
                    encrypted_blob = f.read()

                # 2) Decrypt to get ZSTD-compressed bytes
                decrypted_compressed = decrypt_with_password(
                    encrypted_blob,
                    zip_password
                )

                # 3) Decompress with zstd into the final model file
                dctx = zstd.ZstdDecompressor()
                with open(local_model_path, "wb") as out_file:
                    with dctx.stream_writer(out_file) as writer:
                        writer.write(decrypted_compressed)

            # Load model after successful extraction/decompression
            with open(local_model_path, "rb") as f:
                gc.collect()
                return pickle.load(f)

        except Exception as e:
            logging.warning(
                f"❌ Failed to load model on attempt {attempt} "
                f"(mode={compression_mode}): {e}"
            )

            # clean up the remote file so we can retry a fresh download
            if local_remote_path.exists():
                try:
                    local_remote_path.unlink()
                except Exception:
                    pass

            if attempt >= max_retries:
                raise RuntimeError(
                    f"❌ Failed to load model after {max_retries} attempts: {e}"
                )
