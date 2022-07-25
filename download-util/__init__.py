# 提供给外部调用的接口
from .download_util import download


def download_novel(baseurl, dest):
    return download(baseurl, dest)

