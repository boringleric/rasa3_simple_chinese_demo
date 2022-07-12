import os  
import sys
from rasa.__main__ import main 
import sys


train_flag = False

os.chdir('./test')

if train_flag:    
    sys.argv.append('train')
    main()

else:        
    sys.argv.append('shell')
    #sys.argv.append('run')
    #sys.argv.append('-m')
    #sys.argv.append('models/nlu-20211207-173124.tar.gz')

    sys.argv.append('--endpoints')
    sys.argv.append('endpoints.yml') 
    sys.argv.append('--enable-api')
    sys.argv.append('--debug')

    main()