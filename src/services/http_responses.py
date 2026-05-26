def ok(msg):
    return {"statusCode": 200, "body": msg}


def unauthorised(msg):
    return {"statusCode": 401, "body": msg}


def error(msg):
    return {"statusCode": 500, "body": msg}
