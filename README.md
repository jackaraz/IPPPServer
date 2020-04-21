# IPPPServer
 For job submission in IPPP server

* Requirements

  Python 2.7 or higher...
  Tested in Python 3.6.8

PS: you might want to add IPPPServer to the PYTHONPATH to import it. 
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/IPPPServer
```

or if you dont want to change your bashrc
```python
import sys
sys.path.append('/path/to/IPPPServer')
```


* JobWriter:

Job writer is a tool to avoid submitting job to the same machine with other people. 

```python
from IPPPServer.JobWriter import *

job = JobWriter(path='PATH/WHERE/CODE/LIVES',core_command=['./run_me'])
job.write('myFile',command=['some','args'])
# path and command args are additional to the initial path and command
# and will be attached to the initialized path and command
job.Submit()
```

* JobControl:

This is to control the jobs that are already submitted. JobWriter creates a submit.log
which includes the names and the job ID's of the submitted jobs. If submit.log can not be found
all jobs which are running by the user are taken into account.

```python
from IPPPServer.JobControl import *

job = JobControl(submit_log='PATH/WHERE/SUBMITLOG/LIVES/submit.log')
job.get_status()
```
```bash
BKG_Haajjj_11 is running... Time : 2-02:38:42 Machine : d64
BKG_Haajjj_12 is running... Time : 2-02:38:38 Machine : d65
BKG_Haajjj_13 is running... Time : 2-02:38:33 Machine : d24
BKG_Haajjj_14 is running... Time : 2-02:38:27 Machine : d25
BKG_Haajjj_16 is running... Time : 2-02:38:17 Machine : d26
BKG_Haajjj_18 is running... Time : 2-02:38:07 Machine : d44
BKG_Haajjj_19 is running... Time : 2-02:38:01 Machine : d45
```
```python
job.cancel(BKG_Haajjj_11,BKG_Haajjj_12)
```
```bash
BKG_Haajjj_11 cancelled...
BKG_Haajjj_12 cancelled...
```

It can also run through terminal. To get the status

```bash
./JobControl.py status /PATH/TO/submit.log
./JobControl.py cancel /PATH/TO/submit.log BKG_Haajjj_11 BKG_Haajjj_12
```


# TODO:

- [ ] Integrate with jenkins. This will allow direct python access to the server variables.
- [ ] JobControl needs update. Control sequence from global submit.log is not complete
