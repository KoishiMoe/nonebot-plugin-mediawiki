import csv
from io import StringIO
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# 从 Flandre 里拆出来的解析器，用于解析命令和参数
# TODO: 用argparse吧……谁手搓这玩意
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

def ensure_url_param(url, host_to_check, param_name, param_value):
    """
    Check if URL is under a specific host and add a specific parameter if not present.

    Args:
        url (str): The URL to check
        host_to_check (str): The host to match (e.g., "example.com")
        param_name (str): The parameter to check for and potentially add
        param_value (str): The value to use if parameter needs to be added

    Returns:
        str: The original or modified URL
    """
    parsed_url = urlparse(url)

    # Check if URL is under the specific host
    if parsed_url.netloc == host_to_check or parsed_url.netloc.endswith('.' + host_to_check):
        # Parse query parameters
        query_params = parse_qs(parsed_url.query)

        # Check if the specific parameter exists
        if param_name not in query_params:
            # Parameter doesn't exist, let's add it
            query_params[param_name] = [param_value]

            # Rebuild the query string
            new_query = urlencode(query_params, doseq=True)

            # Rebuild the URL with the new query string
            modified_url = urlunparse(
                (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                 parsed_url.params, new_query, parsed_url.fragment)
            )
            return modified_url

    # Return original URL if host doesn't match or parameter already exists
    return url
