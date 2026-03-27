## unpack ##
def unpack(msg):
    """Splits the received message by the protocol delimiter and extracts the opcode and data parts"""
    new_msg = msg.split("@#2")
    opcode = new_msg[0]
    new_msg = new_msg[1:]
    return opcode, new_msg

## pack ##
def pack_sigh_in(opcode, user_name, password, mail):
    """Constructs a formatted sign-in message string using the provided user credentials and email"""
    return f"{opcode}@#2{user_name}@#2{password}@#2{mail}"

def pack_log_in(opcode, user_name, password):
    """Constructs a formatted login message string with the opcode and user credentials"""
    return f"{opcode}@#2{user_name}@#2{password}"

def pack_update(opcode, mail):
    """Constructs a formatted update message string containing the opcode and the new email address"""
    return f"{opcode}@#2{mail}"

def pack_add_dok(opcode, user_name, dok_path):
    """Constructs a message string to register a new DOK device for a specific user"""
    return f"{opcode}@#2{user_name}@#2{dok_path}"

def pack_restore(opcode, user_name, dok_path):
    """Constructs a restoration request message string with the target user and DOK path"""
    return f"{opcode}@#2{user_name}@#2{dok_path}"

def pack_mide_restore(opcode, user_name):
    """Constructs a message string to request the list of available DOKs for restoration"""
    return f"{opcode}@#2{user_name}"