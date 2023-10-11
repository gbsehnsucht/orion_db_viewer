import re


def split_into_bytes(hex_string):
    byte_list = []

    for i in range(len(hex_string) // 2):
        byte_list.append(hex_string[i * 2:i * 2 + 2])

    return byte_list


def encoding_ascii(ascii_code):
    hex_list = []

    for char in ascii_code:
        if len(hex(ord(char))) > 4:
            hex_list.append(str(char.encode('cp1251'))[4:6])
        elif len(hex(ord(char))) == 3:
            hex_list.append('0' + hex(ord(char))[2:])
        else:
            hex_list.append(hex(ord(char))[2:])

    hex_string = ''.join(reversed(hex_list))
    hex_string = re.sub(r'0[0-9]fe', '00', hex_string).upper()

    return hex_string


def encoding_pass(ascii_code):
    hex_string = encoding_ascii(ascii_code)
    hex_list = split_into_bytes(hex_string)[-1::-1]
    password = ''

    for i in range(int(hex_list[0], 16)):
        char_dec = int(hex_list[i + 1], 16) - int(hex_list[i], 16)
        if char_dec == 0:
            password += b'\xfe'.decode('cp1251') + chr(1)
        elif char_dec > 127:
            password += bytes.fromhex(hex(char_dec)[2:]).decode('cp1251')
        elif char_dec < 0:
            password += bytes.fromhex(hex(char_dec + 256)[2:]).decode('cp1251')
        else:
            password += chr(char_dec)

    return password


def decoding_card(hex_string):

    hex_list = split_into_bytes(hex_string)
    hex_list.append('08')
    code_p = ''

    for byte in reversed(hex_list):
        if int(byte, 16) == 0:
            code_p += b'\xfe'.decode('cp1251') + chr(1)
        elif int(byte, 16) > 127:
            code_p += bytes.fromhex(byte).decode('cp1251')
        else:
            code_p += chr(int(byte, 16))

    return code_p


def decoding_pass(password):

    first_byte = hex(len(password))[2:]
    code_p = chr(int(first_byte, 16)) if len(first_byte) == 2 else chr(int('0' + first_byte, 16))

    for char in password:
        if len(hex(ord(char))) > 4:
            next_byte_int = int(first_byte, 16) + int(str(char.encode('cp1251'))[4:6], 16)
        else:
            next_byte_int = int(first_byte, 16) + ord(char)

        if next_byte_int > 255:
            next_byte_int -= 256

        if next_byte_int == 0:
            code_p += b'\xfe'.decode('cp1251') + chr(1)
        elif next_byte_int > 127:
            code_p += bytes.fromhex(hex(next_byte_int)[2:]).decode('cp1251')
        else:
            code_p += chr(next_byte_int)
        first_byte = hex(next_byte_int)

    return code_p
