import io
import os
import logging

from minio import Minio

from minio.error import NoSuchKey

MINIO_URL        = os.environ.get('MINIO_URL')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
AUTH_BUCKET_NAME = os.environ.get('MINIO_AUTH_BUCKET', 'auth')

logging.debug(F"AUTH_BUCKET: {AUTH_BUCKET_NAME}")
logging.debug(F"MINIO_URL:  {MINIO_URL}")

MINIO_CLIENT = Minio(MINIO_URL,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET_KEY,
                    secure=False)

if not MINIO_CLIENT.bucket_exists(AUTH_BUCKET_NAME):
    MINIO_CLIENT.make_bucket(AUTH_BUCKET_NAME)

def uid_register_job(job_id, metadata=None):
    """
    Register new job

    Args:
        job_id: id of the job to be registered
        metadata: dictionary of metadata(if any)

    Returns: None

    Notes:
        ValueError exception will be raised if
        job has been previously registered

    """

    object_name = str(job_id)

    # look for previous registration
    try:
        MINIO_CLIENT.stat_object(AUTH_BUCKET_NAME, object_name)
        logging.error(F"Job id {object_name} has been registered previously")
        raise ValueError
    except NoSuchKey as err:
        pass

    MINIO_CLIENT.put_object(AUTH_BUCKET_NAME, object_name,
                           data=io.BytesIO(),
                           length=0,
                           metadata=metadata)


def uid_void_job(job_id):
    """
    Void previously registered job

    Args:
        job_id: job identifier

    Returns: None

    Notes:
        If job identifier is not found only warning will logged

    """
    # minioClient = Minio(MINIO_URL,
    MINIO_CLIENT = Minio(MINIO_URL,
                        access_key=MINIO_ACCESS_KEY,
                        secret_key=MINIO_SECRET_KEY,
                        secure=False)

    object_name = str(job_id)

    # look for previous registration
    try:
        # minioClient.stat_object(AUTH_BUCKET_NAME, object_name)
        MINIO_CLIENT.stat_object(AUTH_BUCKET_NAME, object_name)
    except NoSuchKey as err:
        logging.warning(F"Received request to delete unknown job {object_name}")

    # minioClient.remove_object(AUTH_BUCKET_NAME, object_name)
    MINIO_CLIENT.remove_object(AUTH_BUCKET_NAME, object_name)


def uid_validate_job(job_id):
    """
    Validate job

    Args:
        job_id: job identifier

    Returns:
        Job meta_data dictionary if job identifier is valid
        None otherwise

    """

    MINIO_CLIENT = Minio(MINIO_URL,
                        access_key=MINIO_ACCESS_KEY,
                        secret_key=MINIO_SECRET_KEY,
                        secure=False)

    object_name = str(job_id)

    try:
        # obj = minioClient.stat_object(AUTH_BUCKET_NAME, object_name)
        obj = MINIO_CLIENT.stat_object(AUTH_BUCKET_NAME, object_name)
        metadata = {"created_dt": obj.last_modified, **obj.metadata}
        metadata.pop("Content-Type",None)
    except NoSuchKey as err:
        # raised when ID is not found
        logging.info(f'{job_id}: Job ID not found')
        metadata = None

    return metadata

