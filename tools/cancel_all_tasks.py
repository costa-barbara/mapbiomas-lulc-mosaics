# -*- coding: utf-8 -*-
import sys
import os
import subprocess
sys.path.append(os.path.abspath('../gee_toolbox'))
import gee as gee_toolbox

gee_toolbox.init()

accounts = [
    'mapbiomas1',
    'joao',
]

for account in accounts:
    print(account)

    gee_toolbox.switch_user(account)
    gee_toolbox.init()

    print subprocess.Popen("earthengine task cancel all", shell=True,
                           stdout=subprocess.PIPE).stdout.read()
# 
gee_toolbox.switch_user('joao')
gee_toolbox.init()
