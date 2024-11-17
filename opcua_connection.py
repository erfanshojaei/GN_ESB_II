import logging
from opcua import Client

def connectOPCUA():
    """
    Connects to the OPC UA server and returns the root node.
    If the connection fails, logs the error and returns None.
    """
    try:
        # Replace the URL with your OPC UA server address and port
        client = Client("opc.tcp://DESKTOP-761BEPG:4840")  # Port 4840 is the default for OPC UA
        client.connect()
        logging.info("OPC UA client is connected to the server")
        objects = client.get_root_node()
        return objects  # Return the root node or relevant object
    except Exception as e:
        logging.error(f"Failed to connect to OPC UA server: {e}")
        return None
