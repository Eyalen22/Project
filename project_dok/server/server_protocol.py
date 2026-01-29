## unpack ##
def unpack(msg):
    new_msg = msg.split("@#2")
    opcode = new_msg[0]
    new_msg = new_msg[1:]
    return opcode, new_msg


## pack ##
def pack_status(opcode, status):
    return f"{opcode}@#2{status}"

def pack_restore(opcode, file_name, file_path, file_len):
    return f"{opcode}@#2{file_name}@#2{file_path}@#2{file_len}"
