import dill as pickle
import json
import boto3
from datetime import datetime
import os
from io import BytesIO
from pathlib import Path
import botocore

import os
import dill as pickle
import boto3
import requests
from pathlib import Path
from datetime import timedelta
from jrjModelRegistry.mongo import new_model
import pyzipper
import tempfile

import os

from functools import partial


from .mongo import delete_model, search_models_common

if 'JRJ_MODEL_REGISTRY_S3_ENDPOINT' in os.environ:

    s3JrjModelRegistry = boto3.client(
        "s3",
        endpoint_url=f'https://{os.environ['JRJ_MODEL_REGISTRY_S3_ENDPOINT']}',
        region_name=os.environ['JRJ_MODEL_REGISTRY_S3_REGION'],
        aws_access_key_id=os.environ['JRJ_MODEL_REGISTRY_S3_KEY_ID'],
        aws_secret_access_key=os.environ['JRJ_MODEL_REGISTRY_S3_KEY_SECRET'],
        config=botocore.client.Config(signature_version='s3v4')
    )




def registerAJrjModel(model, config):
    modelName = config.get('modelName')
    version = config.get('version')
    modelFileType = config.get('modelFileType', 'pkl')
    modelType = config.get('modelType', 'model')
    config['modelType'] = modelType
    keepLastOnly = config.get('keepLastOnly', False)
    config['keepLastOnly'] = keepLastOnly
    #model.transformer = lambda x: 0

    if not modelName or not version:
        raise ValueError("`modelName` and `version` are required in the config.")

    filename = f"{modelName}__{version}.{modelFileType}"
    zip_filename = f"{filename}.zip"

    # Prepare paths
    local_dir = Path.cwd() / ".~jrjModelRegistry"
    local_dir.mkdir(parents=True, exist_ok=True)
    model_path = local_dir / filename
    zip_path = local_dir / zip_filename

    # Serialize model
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    config['modelSizeBytes'] = model_path.stat().st_size

    # Get password from env
    zip_password = os.environ.get("JRJ_MODEL_REGISTRY_S3_ZIP_PASSWORD")
    if not zip_password:
        raise EnvironmentError("JRJ_MODEL_REGISTRY_S3_ZIP_PASSWORD is not set")

    # Create password-protected ZIP
    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA) as zipf:
        zipf.setpassword(zip_password.encode())
        zipf.setencryption(pyzipper.WZ_AES, nbits=256)
        zipf.write(model_path, arcname=filename)

    config['zippedModelSizeBytes'] = zip_path.stat().st_size
    # Upload to S3 using pre-signed URL
    s3 = boto3.client(
        "s3",
        endpoint_url=f'https://{os.environ["JRJ_MODEL_REGISTRY_S3_ENDPOINT"]}',
        region_name=os.environ["JRJ_MODEL_REGISTRY_S3_REGION"],
        aws_access_key_id=os.environ["JRJ_MODEL_REGISTRY_S3_KEY_ID"],
        aws_secret_access_key=os.environ["JRJ_MODEL_REGISTRY_S3_KEY_SECRET"],
    )

    bucket_name = os.environ['JRJ_MODEL_REGISTRY_S3_BUCKET_NAME']

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
            # print(res)
            if keepLastOnly:
                search_model_result = search_models_common({
                    "search": {
                        "orderBy": [
                            {
                                "createdAt": "desc"
                            }
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
                if search_model_result['count']>0:
                    for mm in search_model_result['data']:
                        s3Url = mm.get('s3Url')
                        _id = str(mm.get('_id'))
                        print(f"deleting model {_id} with s3Url {s3Url}")
                        if s3Url:
                            deleteAJrjModelAsset(s3Url)
                        delete_model(_id)
            return res
        else:
            print(f"❌ Upload failed via PUT: {response.status_code} {response.text}")
            return None

    except Exception as e:
        print(f"❌ Failed to generate URL or upload: {e}")
        return None
    finally:
        for p in [model_path, zip_path]:
            try:
                p.unlink()
            except Exception as cleanup_err:
                print(f"⚠️ Failed to delete {p}: {cleanup_err}")
        # return res

def deleteAJrjModelAsset(s3AssetPath):
    """
    Deletes a model asset from S3 using the given s3AssetPath (e.g., 'my-bucket/my-model__v1.pkl.zip')
    """
    try:
        bucket_name, key = s3AssetPath.split('/', 1)

        s3 = boto3.client(
            "s3",
            endpoint_url=f'https://{os.environ["JRJ_MODEL_REGISTRY_S3_ENDPOINT"]}',
            region_name=os.environ["JRJ_MODEL_REGISTRY_S3_REGION"],
            aws_access_key_id=os.environ["JRJ_MODEL_REGISTRY_S3_KEY_ID"],
            aws_secret_access_key=os.environ["JRJ_MODEL_REGISTRY_S3_KEY_SECRET"],
        )

        s3.delete_object(Bucket=bucket_name, Key=key)
        print(f"🗑️ Deleted s3://{bucket_name}/{key}")
        return True

    except Exception as e:
        print(f"❌ Failed to delete S3 asset '{s3AssetPath}': {e}")
        return False


def loadAJrjModel(modelObj):
    """
    Loads a model from a password-protected ZIP file stored in S3 (or from local cache if already downloaded and extracted).
    modelObj must contain:
      - 's3Url': str, e.g. 'bucket-name/path/to/model__version.pkl.zip'
    """
    s3_url = modelObj.get("s3Url")
    if not s3_url or "/" not in s3_url:
        raise ValueError("Invalid or missing `s3Url` in modelObj")

    bucket_name, key = s3_url.split("/", 1)
    zip_password = os.environ.get("JRJ_MODEL_REGISTRY_S3_ZIP_PASSWORD")
    if not zip_password:
        raise EnvironmentError("JRJ_MODEL_REGISTRY_S3_ZIP_PASSWORD is not set")

    # Extract file names
    zip_filename = Path(key).name
    model_filename = zip_filename.replace(".zip", "")
    # Local paths
    local_dir = Path.cwd() / ".~jrjModelRegistry"
    local_dir.mkdir(parents=True, exist_ok=True)

    local_zip_path = local_dir / zip_filename
    local_model_path = local_dir / model_filename

    # If already extracted, just load it
    if local_model_path.exists():
        try:
            with open(local_model_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load cached model. Redownloading... ({e})")

    # Set up S3 client
    s3 = boto3.client(
        "s3",
        endpoint_url=f'https://{os.environ["JRJ_MODEL_REGISTRY_S3_ENDPOINT"]}',
        region_name=os.environ["JRJ_MODEL_REGISTRY_S3_REGION"],
        aws_access_key_id=os.environ["JRJ_MODEL_REGISTRY_S3_KEY_ID"],
        aws_secret_access_key=os.environ["JRJ_MODEL_REGISTRY_S3_KEY_SECRET"],
    )

    # Download ZIP if not already downloaded
    if not local_zip_path.exists():
        try:
            with open(local_zip_path, "wb") as f:
                s3.download_fileobj(bucket_name, key, f)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to download ZIP from S3: {e}")

    # Extract ZIP
    try:
        with pyzipper.AESZipFile(local_zip_path, 'r') as zf:
            zf.setpassword(zip_password.encode())
            with open(local_model_path, "wb") as out_file:
                out_file.write(zf.read(model_filename))
    except Exception as e:
        raise RuntimeError(f"❌ Failed to extract ZIP file: {e}")

    # Load model
    try:
        with open(local_model_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load model: {e}")