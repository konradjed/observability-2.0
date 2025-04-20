import logging
from pythonjsonlogger import jsonlogger

def setup_logging(service_name: str):
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    handler.setFormatter(jsonlogger.JsonFormatter(fmt))
    root.handlers = [handler]

    # Optionally, you can add service_name to every log
    logging.LoggerAdapter(root, {"service": service_name})