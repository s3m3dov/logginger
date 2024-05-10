DEFAULT_FMT = "%(levelprefix)s %(asctime)s (%(name)s) %(message)s"
UVICORN_DEFAULT_FMT = "%(levelprefix)s %(message)s"
UVICORN_ACCESS_FMT = (
    '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)
CUSTOM_ACCESS_FMT = '%(levelprefix)s %(asctime)s (%(name)s) %(client_addr)s - "%(request_line)s" %(status_code)s'
