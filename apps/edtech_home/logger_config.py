import logging


def setup_logger():
    # Create or get the logger
    logger = logging.getLogger("edtech_logger")

    # Set the logging level to DEBUG
    logger.setLevel(logging.DEBUG)

    # Create a console handler to output logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Define the logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger if it doesn't already have handlers
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


# Initialize the logger instance
logger = setup_logger()
