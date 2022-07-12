import os  
import sys
from rasa.__main__ import main
import sys


train_flag = False

os.chdir('./test')
     
sys.argv.append('run')
sys.argv.append('actions')
sys.argv.append('--actions')
sys.argv.append('actions')
sys.argv.append('-vv')

main()