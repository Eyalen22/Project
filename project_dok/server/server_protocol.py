"""Provides utility functions for packing and unpacking messages based on the @#2 protocol delimiter"""

## unpack ##
def unpack(msg):
    """Splits an incoming message string into an opcode and its subsequent parameters using the protocol delimiter"""
    new_msg = msg.split("@#2")
    opcode = new_msg[0]
    new_msg = new_msg[1:]
    return opcode, new_msg


## pack ##
def pack_status(opcode, status):
    """Formats a status response message according to the communication protocol"""
    return f"{opcode}@#2{status}"

def pack_restore(opcode, file_name, file_path, file_len):
    """Packs file metadata into a restore command string for client-side processing"""
    return f"{opcode}@#2{file_name}@#2{file_path}@#2{file_len}"

def pack_add_dok(opcode, status, mail):
    """Constructs a response message for DOK registration including the user's email address"""
    return f"{opcode}@#2{status}@#2{mail}"

def pack_get_doks_name(opcode, msg):
    """Packs a list of registered DOK names into a response message"""
    return f"{opcode}@#2{msg}"