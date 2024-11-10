from opcua import Client

objects = None

def connectOPCUA():
    global objects
    client = Client("opc.tcp://DESKTOP-761BEPG:4840")
    client.connect()
    print("communication is OK")

    objects = client.get_root_node()


if __name__=='__main__':

    connectOPCUA()




