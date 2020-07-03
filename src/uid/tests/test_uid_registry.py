from uid.service.uid_registry import uid_register_job, uid_void_job, uid_validate_job


def test_uid_register_job():

    uid_register_job(1234)
    uid_void_job(1234)

    uid_register_job(1234,metadata={"ip": "0.0.0.0"})
    uid_void_job(1234)

def test_uid_void_job():
    uid_void_job(123456)

def test_uid_validate_job():
    uid_void_job(123456)
    uid_register_job(123456, metadata={"ip": "0.0.0.0"})
    print("\n")
    print(uid_validate_job(123456))
