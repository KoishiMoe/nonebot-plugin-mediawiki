import sys

'''
代码来自 pymediawiki 库（以MIT许可证开源），并根据bot的实际需要做了一些修改
该库的Github地址：https://github.com/barrust/mediawiki
许可证：https://github.com/barrust/mediawiki/blob/master/LICENSE
'''


def str_or_unicode(text):
    """ handle python 3 unicode """
    encoding = sys.stdout.encoding
    return text.encode(encoding).decode(encoding)
