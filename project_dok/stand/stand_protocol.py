## unpack ##
def unpack(msg):
    new_msg = msg.split("@#2")
    opcode = new_msg[0]
    new_msg = new_msg[1:]
    return opcode, new_msg



## pack ##
def pack_sigh_in(opcode, user_name, password, mail):
    return f"{opcode}@#2{user_name}@#2{password}@#2{mail}"

def pack_log_in(opcode, user_name, password):
    return f"{opcode}@#2{user_name}@#2{password}"

def pack_update(opcode, mail):
    return f"{opcode}@#2{mail}"

def pack_add_dok(opcode, user_name, dok_path):
    return f"{opcode}@#2{user_name}@#2{dok_path}"

def pack_restore(opcode, user_name, dok_path):
    return f"{opcode}@#2{user_name}@#2{dok_path}"
