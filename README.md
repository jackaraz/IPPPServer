# IPPP-Server
 For job submission in IPPP server

* Requirements

  Python 2.7 or higher...
  Tested in Python 3.6.8

* JobWriter:

Job writer is a tool to avoid submitting job to the same machine with other people. 

```python
import sys
sys.path.append('IPPP-Server')
from JobWriter import *

job = JobWriter('PATH/WHERE/CODE/LIVES',['./run_me'])
job.write('myFile',command=['some','args'])
job.Submit()
```

* JobControl:

This is to control the jobs that are already submitted. JobWriter creates a submit.log
which includes the names and the job ID's of the submitted jobs. If submit.log can not be found
all jobs which are running by the user are taken into account.

```python
import sys
sys.path.append('IPPP-Server')
from JobWriter import *

job = JobControl(submit_log='PATH/WHERE/SUBMITLOG/LIVES/submit.log')
job.get_status()

>BKG_Haajjj_11 is running... Time : 1-23:29:55
>BKG_Haajjj_12 is running... Time : 1-23:29:51
>BKG_Haajjj_13 is running... Time : 1-23:29:46
>BKG_Haajjj_14 is running... Time : 1-23:29:40
>BKG_Haajjj_16 is running... Time : 1-23:29:30
>BKG_Haajjj_18 is running... Time : 1-23:29:20
>BKG_Haajjj_19 is running... Time : 1-23:29:14

job.cancel(BKG_Haajjj_11,BKG_Haajjj_12)

>BKG_Haajjj_11 cancelled...
>BKG_Haajjj_12 cancelled...
```

It can also run through terminal. To get the status

```bash
python JobWriter.py status /PATH/TO/submit.log
python JobWriter.py cancel /PATH/TO/submit.log BKG_Haajjj_11 BKG_Haajjj_12
```