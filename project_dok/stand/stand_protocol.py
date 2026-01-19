## unpack ##
def unpack(msg):
    new_msg = msg.spilt("@#2")[0]
    opcode = new_msg[0]
    new_msg = new_msg[1:]
    unpacked = None

    if opcode == ["00", "01", "02", "06"]:
         unpacked = unpack_status(new_msg)
    elif opcode == "04":
         unpacked = unpack_restore(new_msg)

    return opcode, unpacked

def unpack_status(new_msg):
    status = new_msg[0]
    return status

def unpack_restore(new_msg):
    file_name = new_msg[0]
    file_path = new_msg[1]
    file_len = new_msg[2]
    file = new_msg[4]
    return file_name, file_path, file_len, file

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

