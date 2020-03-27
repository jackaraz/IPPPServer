#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:13:27 2020

@author  : jackaraz
@contact : Jack Y. Araz <jackaraz@gmail.com>
"""

import os, logging
from .JobControl import JobControl


class JobWriter:
    def __init__(self,path=os.getcwd(),core_command='\n', **kwargs):
        """
            Configure initial job writer
        """
        self.logger = logging.getLogger(__name__)
        if kwargs.get('debug',False):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        if not os.path.isdir(path):
            raise Warning('Hmm can not find '+path)
        self.core_path = path
        # path where the initial code to be run lives
        if type(core_command) == str:
            self.core_command = [core_command]
        elif type(core_command) == list:
            self.core_command = core_command
        # core command which is same for all iterations of the job

        self.mail       = kwargs.get('mail','mailname@durham.ac.uk')
        self.log_path   = os.path.join(os.path.expanduser('~').replace('home','batch'),'LOG')
        self.submit_log = os.path.join(self.log_path,'submit.log')

        if not os.path.isdir(self.log_path):
            os.mkdir(self.log_path)

        try:
            self.control   = JobControl().update_log()
        except:
            raise Warning("Check logging...")
        self.JobIDinit = 0

    def write(self,*args,**kwargs):
        if args == []:
            jobID = max([int(x.split('.sh')[0].split('_')[1]) \
                            for x in os.listdir('.') if 'jobID_' in x]+\
                            [self.JobIDinit])+1
            self.filename = 'jobID_{:03d}'.format(jobID)
        else:
            self.filename = args[0]
        file = open(self.filename+'.sh','w')
        file.write('#!/bin/sh\n')
        if self.mail != 'mailname@durham.ac.uk':
            file.write('#SBATCH --mail-type=ALL\n')
            file.write('#SBATCH --mail-user='+self.mail+'\n')

        file.write('#SBATCH --error="'+os.path.join(self.log_path,
                                                    self.filename+'.err')+'"\n')
        file.write('#SBATCH --output="'+os.path.join(self.log_path,
                                                     self.filename+'.out')+'"\n\n')
        occupied = ','.join(self.occupied_list())
        if occupied != '':
            file.write('#SBATCH --exclude='+occupied+'\n\n')
        else:
            file.write('# nothing to exclude \n\n')

        path = os.path.join(self.core_path,kwargs.get('path',''))
        file.write('cd '+path+'\n')
        run_command =  kwargs.get('command',[])
        if type(run_command) == str:
            run_command = [run_command]
        run_command = self.core_command + run_command
        file.write(' '.join(run_command)+'\n')
        file.write('exit 0\n')
        file.close()
        return True

    def occupied_list(self):
        """
            Creates a list of the computers that are already have jobs.
            PS: if the server is overloaded, workstations will not be excluded.
        """
        os.system('squeue > .log.txt')
        with open('.log.txt','r') as f:
            ls = f.readlines()
        ls = ls[1:len(ls)]
        ls_temp = [x.split()[len(x.split())-1] for x in ls if not '(' in x]
        ls = []
        os.remove('.log.txt')
        for i in ls_temp:
            if not i in ls:
                ls.append(i)
        if len(ls) >= 40:
            return [x for x in ls if 'ip3-ws' not in x]
        return ls


    def update_exclude(self,filename):
        if filename.endswith('.sh'):
            filename = filename.split('.sh')[0]
        if os.path.isfile(filename+'.sh'):
            with open(filename+'.sh', 'r') as f:
                file_to_modify = f.readlines()
            for i in range(len(file_to_modify)):
                if file_to_modify[i].startswith('#SBATCH --exclude=') or \
                   file_to_modify[i].startswith('# nothing to exclude'):
                    occupied = ','.join(self.occupied_list())
                    if occupied != '':
                        file_to_modify[i] = '#SBATCH --exclude='+occupied+'\n\n'
                    else:
                        file_to_modify[i] = '# nothing to exclude \n\n'
                    break
            rewrite = open(filename+'.sh','w')
            rewrite.writelines(file_to_modify)
            rewrite.close()
        else:
            print('Can not find '+filename+'.sh')


    def Submit(self,remove_after_submission=False, **params):
        filename = params.get('filename',self.filename)
        if filename.endswith('.sh'):
            filename = filename.split('.sh')[0]
        os.system('sbatch '+filename+'.sh > .temp.txt')
        with open('.temp.txt','r') as f:
            temp = f.readlines()
        if temp == []:
            os.remove('.temp.txt')
            print('Can not retreive job information for '+filename)
            print('Please double check if its submitted properly: ')
            os.system('squeue -u '+os.environ['LOGNAME'])
        else:
            temp = temp[0].split()[len(temp[0].split())-1]
            submit_log = open(self.submit_log,'a+')
            submit_log.write(filename+' '+temp+'\n')
            submit_log.close()
            os.remove('.temp.txt')
            if remove_after_submission:
                os.remove(filename+'.sh')
                self.JobIDinit += 1




#if __name__=='__main__':
#    import sys
#    log = logging.getLogger(__name__)
#    log.setLevel(logging.INFO)
#    path = sys.argv[1]
#    if not os.path.isdir(path):
#        
