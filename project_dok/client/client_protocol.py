## pack ##


def pack_back_up(opcode, file_name, file_path, file_len, user_name, file):
    return f"{opcode}@#2{file_name}@#2{file_path}@#2{file_len}@#2{user_name}@#2{file}"
