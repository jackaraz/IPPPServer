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
        self.logger = logging.getLogger(__name__)
        if kwargs.get('debug',False):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.submit_log = []

        self.log_path = os.path.join(os.path.expanduser('~').replace('home','batch'),'LOG')
        self.log_file = os.path.join(self.log_path,'submit.log')

        if os.path.isfile(self.log_file):
            with open(self.log_file,'r') as f:
                submit_log = f.readlines()
            self.submit_log += [(x.split()[0],int(x.split()[1])) for x in submit_log if len(x.split())<4]
            self.submit_log += [(x.split()[0],int(x.split()[1]),x.split()[2],x.split()[3]) for x in submit_log if len(x.split())==4]

    def get_status(self, print_out=False):
        if self.submit_log == []:
            if print_out:
                pass
            else:
                return []
        os.system('squeue > .tmp.log')
        with open('.tmp.log','r') as f:
            jobs = f.readlines()
        os.remove('.tmp.log')
        jobs  = jobs[1:]
        jobID = [int(x.split()[0]) for x in jobs[1:]]
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
        submit_log_ID = [x[1] for x in self.submit_log]
        for name, ID, tm, ws in zip(job_names,self.myJobID, time, machine):
            if ID in submit_log_ID:
                log.append((ID, name, tm, ws))


        if print_out:
            self._print_status([x for x in log if x[0] in self.myJobID])
            return 
        return log


    def _print_status(self, log):
        log4 = [x for x in log if len(x)==4]
        log2 = [x for x in log if len(x)< 4]
        for ID, name, time, machine in log4:
            print(name+' is running... Time : '+time+' Machine : '+machine)
        for ID, name in log2:
            print(name+' is running...')


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
                output.write(name+' '+str(ID)+' '+time+' '+machine+'\n')
            output.close()
            return True
        return True




if __name__=='__main__':
    import sys
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    if sys.argv[1].startswith('cancel'):
        if os.path.isfile(sys.argv[2]):
            job = JobControl(submit_log=sys.argv[2])
            if len(sys.argv) > 3:
                job.cancel(sys.argv[3:])
            else:
                job.cancel()
        else:
            log.error('Can not find '+sys.argv[2])
    elif sys.argv[1].startswith('status'):
        if os.path.isfile(sys.argv[2]):
            job = JobControl(submit_log=sys.argv[2])
            job.get_status(print_out=True)
        else:
            print('Can not find '+sys.argv[2])
    else:
        print('No option called '+sys.argv[1])





