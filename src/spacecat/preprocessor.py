from typing import List, Union, Tuple, Dict
from re import sub
from re import compile as regex_compile

comment_pattern = regex_compile(r";.*")
org_pattern = regex_compile(r"(?<=org )\w+")
string_pattern = regex_compile(r"\"\w+\"|'\w+'")
three_register_operations = ["addi", "addf", "or", "xor", "and"]
three_register_op_codes = {"addi": "5", "addf": "6", "or": "7", "and": "8", "xor": "9"}

def convert_numeral(string: str) -> str:
    """
    Convert a assembly numeral into a hexadecimal numeral
    :param string: A string representation of a simpSim numeral
    :return: Hexadecimal representation of the numeral
    """
    return_num: int = 0
    is_pointer: bool = string.startswith("[") and string.endswith("]")
    string = string.strip("[").strip("]")
    replacement_dict = {
        'b': 2,
        '0x': 16,
        '$': 16,
        'h': 16,
        '-': 10,
        '': 10
    }
    for identifier in replacement_dict:
        if identifier in string:
            string = string.replace(identifier, '')
            return_num = int(string, base=replacement_dict[identifier])
            break
    if is_pointer:  # If number is a pointer.
        return "[" + format(return_num, "02X") + "]"
    return format(return_num, "02X")


def __is_label(string: str) -> bool:
    """
    Return if a given string is a label declaration.
    :param string:
    :return:
    """
    return string.endswith(":") and '"' not in string and "'" not in string


def __is_org(string: str) -> bool:
    """
    Return if a given string is an org directive
    :param string: String to check for org.
    :return: True if org.
    """
    return string.startswith("org ")


def __split_label(string: str) -> List[str]:
    """
    Return the name of label from a label statement
    :param string:
    :return:
    """
    return string.split(":")


def __org_compile(string: str) -> str:
    """
    Return the memory address from an org statement
    :param string: ex: org 16
    :return: Memory address in hex, if there is no address, return ""
    """
    if match := org_pattern.findall(string):
        number_hex: str = convert_numeral(match[0])
        return number_hex
    else:
        return ""


def convert_numerals_hexadecimal(string: str) -> str:
    """
    Convert all decimal, binary and hexadecimals numbers to hexadecimal numbers for easy conversion.
    :param string: String to decode
    :return: The converted string.
    """
    converted_string = ""
    for line in string.split("\n"):
        if " " not in line:
            converted_string += line + "\n"
            continue
        mnemonic, operands = line.split(" ")
        operands = operands.split(',')
        for i, operand in enumerate(operands):
            try:
                operands[i] = convert_numeral(operand)
            except ValueError:
                continue
        converted_string += ' '.join((mnemonic, ','.join(operands))) + "\n"
    return converted_string


def __strip_comments_spaces_tabs(string: str) -> str:
    """
    Strip assembly comments and spaces as well as tabs from a string
    :param string:
    :return:
    """
    string_substiuted: str = ""
    for line in string.split("\n"):
        if line == "":
            continue
        else:
            substitute: str = sub(comment_pattern, "", line)
            substitute = substitute.strip()
            substitute = substitute.replace("\t", "RESERVED_TAB_CHAR", 1)
            substitute = substitute.replace("\t", "")
            substitute = substitute.replace("RESERVED_TAB_CHAR", " ")
            substitute = substitute.replace(" ", "RESERVED_SPACE_CHAR", 1)
            substitute = substitute.replace(" ", "")
            substitute = substitute.replace("RESERVED_SPACE_CHAR", " ")
            string_substiuted += substitute + "\n"
    return string_substiuted


def __parse_db(db_exp: str) -> List[Union[str, int]]:
    """
    Parse a DB directive returning its contents as a list.
    :param db_exp: DB directive command.
    :return: Contents of the db as the directive.
    """
    db_exp_ = db_exp.split(" ", 1)[1]
    db_params = [eval(param) for param in db_exp_]
    params: List[Union[str, int]] = []
    for param_ in db_params:
        if isinstance(param_, str):
            params.extend(char for char in param_)
        else:
            params.append(param_)  # TO-DO: Error regarding number overflows in DB.
    return params


def __parse_expression(memory_ptr: int, expression: str) -> int:
    """
    Parse an expression to see where the Assembler will place it in the memory/how it will effect the memory.
    :param memory_ptr: Current location of the memory.
    :param expression: A directive or an instruction.
    :return: the location of the pointer after calculations.
    """
    if "db " in expression:
        return memory_ptr + len(__parse_db(expression))
    elif "org " in expression:
        return int(__org_compile(expression), base=16)
    else:
        return memory_ptr + 2


def __decide_locations(lines: List[str]) -> Tuple[List[str], Dict[str, int]]:
    """
    Decide the memory addresses each label should point to.
    :param lines: Lines in the source file in a list.
    :return: A tuple of lines without label declarations and a dictionary of labels to their corresponding
        addresses
    """
    label_names: List[str] = []
    label_locations: List[int] = []
    lines_no_label_defs = []
    memory_pointer = -2
    for line in lines:
        if __is_label(line):
            label_name, *expression = __split_label(line)
            label_names.append(label_name)
            label_locations.append(memory_pointer + 2)
            if expression != ['']:
                exp = expression[0]
                memory_pointer = __parse_expression(memory_pointer, exp)
                label_locations.pop()
                label_locations.append(memory_pointer)
                lines_no_label_defs.append(exp)
        else:
            memory_pointer = __parse_expression(memory_pointer, line)
            lines_no_label_defs.append(line)
    label_locations_ = {label_names[i]: label_locations[i] for i in range(len(label_locations))}
    return lines_no_label_defs, label_locations_


def __attempt_replace(line_args: str, labels_locs: Dict[str, int]) -> str:
    """
    Atttempt to replace a label with its memory address.
    :param line_args: Part of the line including the arguments.
    :param labels_locs: Labels and their memory addresses.
    :return: Line with the label replaced to its memory address.
    """
    for label in labels_locs:
        if label in line_args:
            line_args = line_args.replace(label, f"{labels_locs[label]:02X}h")
            return line_args
    return line_args


def __replace_labels(lines_no_label_defs: List[str], label_locations: Dict[str, int]) -> List[str]:
    """
    Replace the labels with implicit memory addresses
    :param lines_no_label_defs: Lines with no label definitions as a list.
    :param label_locations: Labels and their corresponding locations as a dictionary.
    :return: List of lines without labels.
    """
    new_lines: List[str] = []
    for line in lines_no_label_defs:
        mnemonic, *args = line.split(" ", 1)
        if args:
            line = mnemonic + " " + __attempt_replace(args[0], label_locations)
        new_lines.append(line)
    return new_lines


def __strip_labels(string: str) -> str:
    """
    Delete label declarations and replace label references with explicit memory locations.
    :param string:
    :return:
    """
    lines = list(filter(lambda line_: line_ != "", string.split("\n")))
    lines_no_label_defs, label_locations = __decide_locations(lines)
    lines_no_labels = __replace_labels(lines_no_label_defs, label_locations)
    return '\n'.join(lines_no_labels)


def preprocess(string: str) -> str:
    """
    Clear a string by preprocessing it into a simpler assembly form.
    :param string: String to preprocess.
    :return: Cleaned string.
    """
    cleaned_string = string.lower()
    cleaned_string = __strip_comments_spaces_tabs(cleaned_string)
    cleaned_string = __strip_labels(cleaned_string)
    cleaned_string = convert_numerals_hexadecimal(cleaned_string)
    return cleaned_string

