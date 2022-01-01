# -*- coding: UTF-8 -*-

import os

# 檢查path是否為一個合法的路徑，如果不是就新建一個
def isPATH(path):
    if not os.path.isdir(path):
        os.makedirs(path)
