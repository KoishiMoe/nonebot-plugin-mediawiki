import csv
from io import StringIO


# 从 Flandre 里拆出来的解析器，用于解析命令和参数
def process_command(command: str, user_input: str) -> tuple:
    """
    :param command: 命令本体
    :param user_input: 用户输入
    :return: 处理后的参数元组，格式为([无名参数列表], {命名参数字典})
    """
    user_input = user_input.strip()
    command = command.strip()
    if user_input.startswith(command):
        user_input = user_input[len(command):].lstrip()  # 去掉命令本体，用这个写法是为了与旧版python兼容

    f = StringIO(user_input)
    reader = csv.reader(f, delimiter=" ", escapechar="\\", skipinitialspace=True)
    input_list = []
    for i in reader:
        input_list += [j for j in i if j]

    out_list = []
    out_dict = {}

    i = 0
    while i < len(input_list):
        if _startswith(input_list[i], "-－"):
            next_item = _get_item(input_list, i + 1)
            if not _startswith(next_item, "-－"):
                out_dict[input_list[i].lstrip("-－")] = next_item if next_item is not None else True
                # 此处将只提供参数名不提供值的认为是True（简化语法）
                i += 2
            else:
                out_dict[input_list[i].lstrip("-－")] = True
                i += 1
        else:
            out_list.append(input_list[i])
            i += 1

    return out_list, out_dict


def _get_item(ls: list, item: int):
    """
    为列表实现类似字典的get方法
    :param ls: 要查询的列表
    :param item: 元素的下标
    :return: 若元素存在，返回该元素；否则返回None
    """
    try:
        return ls[item]
    except IndexError:
        return None


def _startswith(string: str, prefix: str) -> bool:
    """
    替换原版的startswith方法
    :param string: 要检测的字符串
    :param prefix: 要检测的前缀，字符串中的每个字符都将被单独检测
    :return: 判定结果
    """
    if not string:
        return False
    for i in prefix:
        if string.startswith(i):
            return True
    return False
