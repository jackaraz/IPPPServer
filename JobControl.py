#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:00:25 2020

@author  : jackaraz
@contact : Jack Y. Araz <jackaraz@gmail.com>
"""

import os

class JobControl:
    def __init__(self,**kwargs):
        self.submit_log = []
        if os.path.isfile(kwargs.get('submit_log','submit.log')):
            with open(kwargs.get('submit_log','submit.log'),'r') as f:
                submit_log = f.readlines()
            self.submit_log = [(x.split()[0],int(x.split()[1])) for x in submit_log]

    def get_status(self):
        os.system('squeue > tmp.log')
        with open('tmp.log','r') as f:
            jobs = f.readlines()
        os.remove('tmp.log')
        jobs  = jobs[1:]
        jobID   = [int(x.split()[0]) for x in jobs[1:]]
        me = os.environ.get('LOGNAME',False)
        self.myJobID = []
        time = []
        if me != False:
            self.myJobID = [int(x.split()[0]) for x in jobs if x.split()[3] == me]
            time         = [x.split()[5] for x in jobs if x.split()[3] == me]
            job_names    = [x.split()[2] for x in jobs if x.split()[3] == me]
            machine      = [x.split()[7] for x in jobs if x.split()[3] == me]
        else:
            self.myJobID = jobID
            time         = [x.split()[5] for x in jobs]
            job_names    = [x.split()[2] for x in jobs]
            machine      = [x.split()[7] for x in jobs]

        log = []
        if self.submit_log == []:
            for name, ID in zip(job_names,self.myJobID):
                log.append((name,ID))
        else:
            log = self.submit_log

        for name, ID in log:
            if ID in self.myJobID:
                print(name+' is running... Time : '+time[self.myJobID.index(ID)]+\
                      ' Machine : '+machine[self.myJobID.index(ID)])

    def cancel(self,*args):
        for name, ID in self.submit_log:
            if args != []:
                if name in args:
                    try:
                        os.system('scancel '+str(ID))
                        print(name+' cancelled...')
                    except:
                        print('Can not cancel '+name)
            else:
                try:
                    os.system('scancel '+str(ID))
                    print(name+' cancelled...')
                except:
                    print('Can not cancel '+name)
        return True





if __name__=='__main__':
    import sys
    if sys.argv[1].startswith('cancel'):
        if os.path.isfile(sys.argv[2]):
            job = JobControl(submit_log=sys.argv[2])
            if len(sys.argv) > 3:
                job.cancel(sys.argv[3:])
            else:
                job.cancel()
        else:
            print('Can not find '+sys.argv[2])
    elif sys.argv[1].startswith('status'):
        if os.path.isfile(sys.argv[2]):
            job = JobControl(submit_log=sys.argv[2])
            job.get_status()
        else:
            print('Can not find '+sys.argv[2])





