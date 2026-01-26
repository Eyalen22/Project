## unpack ##
def unpack(msg):
    new_msg = msg.spilt("@#2")[0]
    opcode = new_msg[0]
    new_msg = new_msg[1:]
    unpacked = None

    if opcode == "00":
         unpacked = unpack_sigh_in(new_msg)
    elif opcode == "01":
         unpacked = unpack_log_in(new_msg)
    elif opcode == "02":
         unpacked = unpack_update(new_msg)
    elif opcode == "03":
         unpacked = unpack_back_up(new_msg)
    elif opcode == "04":
         unpacked = unpack_restore(new_msg)
    elif opcode == "06":
         unpacked = unpack_add_dok(new_msg)

    return opcode, unpacked

def unpack_sigh_in(new_msg):
    user_name = new_msg[0]
    password = new_msg[1]
    mail = new_msg[2]
    return user_name, password, mail

def unpack_log_in(new_msg):
    user_name = new_msg[0]
    password = new_msg[1]
    return user_name, password

def unpack_update(new_msg):
    mail = new_msg[0]
    return mail

def unpack_back_up(new_msg):
    file_name = new_msg[0]
    file_path = new_msg[1]
    user_name = new_msg[2]
    full_path = new_msg[3]
    return file_name, file_path, user_name, full_path

def unpack_restore(new_msg):
    user_name = new_msg[0]
    dok_path = new_msg[1]
    return user_name, dok_path

def unpack_add_dok(new_msg):
    user_name = new_msg[0]
    dok_path = new_msg[1]
    return user_name, dok_path

## pack ##
def pack_status(opcode, status):
    return f"{opcode}@#2{status}"

def pack_restore(opcode, file_name, file_path, file_len):
    return f"{opcode}@#2{file_name}@#2{file_path}@#2{file_len}"
