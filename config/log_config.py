from logging import config


def logger_config():
    log_config = {
        "version": 1,
        "root": {"handlers": ["console"], "level": "DEBUG"},
        "handlers": {
            "console": {
                "formatter": "std_out",
                "class": "logging.StreamHandler",
                "level": "INFO",
            }
        },
        "formatters": {
            "std_out": {
                "format": "%(asctime)s %(levelname)s - "
                          "%(module)s.%(funcName)s:"
                          "%(lineno)d - %(message)s",
                "datefmt": "%d-%m-%Y %I:%M:%S",
            }
        },
    }

    config.dictConfig(log_config)
