import logging
import time
from opcua import Client

def connectOPCUA():
    """
    Connects to the OPC UA server and returns the root node.
    Implements retry mechanism if connection fails.
    Returns the root node if successful, else None.
    """
    hostname = "DESKTOP-761BEPG"  # Hostname of the OPC UA server
    port = 4840  # Port number (default for OPC UA)
    retries = 3  # Number of retries
    delay = 5  # Delay between retries in seconds
    opcua_url = f"opc.tcp://{hostname}:{port}"

    for attempt in range(retries):
        try:
            logging.info(f"Attempting to connect to OPC UA server at {opcua_url} (Attempt {attempt + 1}/{retries})")
            client = Client(opcua_url)
            client.connect()
            logging.info("OPC UA client successfully connected to the server")

            # Return the root node if connection is successful
            objects = client.get_root_node()
            return objects
        except Exception as e:
            logging.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    logging.error("Failed to connect to OPC UA server after multiple attempts.")
    return None