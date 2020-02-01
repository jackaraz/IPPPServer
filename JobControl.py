#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:00:25 2020

@author  : jackaraz
@contact : Jack Y. Araz <jackaraz@gmail.com>
"""

import os, logging

class JobControl:
    def __init__(self,**kwargs):
        self.log = logging.getLogger(__name__)
        if kwargs.get('debug',False):
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)
        self.submit_log = []
        self.log_file   = kwargs.get('submit_log','submit.log')
        if os.path.isfile(self.log_file):
            with open(kwargs.get('submit_log','submit.log'),'r') as f:
                submit_log = f.readlines()
            self.submit_log = [(x.split()[0],int(x.split()[1])) for x in submit_log]

    def get_status(self, print_out=False):
        if self.submit_log == []:
            if print_out:
                pass
            else:
                return []
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
            for name, ID, tm, ws in zip(job_names,self.myJobID, time, machine):
                log.append((ID, name, tm, ws))
        else:
            log = self.submit_log

        if print_out:
            for ID, name, time, machine in log:
                if ID in self.myJobID:
                    self.log.info(name+' is running... Time : '+time+\
                                  ' Machine : '+machine)
            return 
        return log

    def cancel(self,*args):
        for name, ID in self.submit_log:
            if args != []:
                if name in args:
                    try:
                        os.system('scancel '+str(ID))
                        self.log.info(name+' cancelled...')
                    except:
                        self.log.warning('Can not cancel '+name)
            else:
                try:
                    os.system('scancel '+str(ID))
                    self.log.info(name+' cancelled...')
                except:
                    self.log.warning('Can not cancel '+name)
        return True

    def get_log(self,filename):
        if os.path.isfile(os.path.join(os.path.expanduser('~').replace('home','batch'),
                                       'LOG',filename)):
            os.system(os.environ.get('EDITOR','vi')+' '+\
                      os.path.join(os.path.expanduser('~').replace('home','batch'),
                                   'LOG',filename))
        elif os.path.isfile(filename):
            os.system(os.environ.get('EDITOR','vi')+' '+filename)

    def update_log(self):
        log = self.get_status()
        if log == [] and os.path.isfile(self.log_file):
            os.remove(self.log_file)
        elif os.path.isfile(self.log_file):
            output = open(self.log_file, 'w')
            for ID, name, time, machine in log:
                output.write(name+' '+str(ID)+'\n')
            output.close()
            return True
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
            job.get_status(print_out=True)
        else:
            print('Can not find '+sys.argv[2])





