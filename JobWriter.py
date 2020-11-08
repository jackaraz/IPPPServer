#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:13:27 2020

@author  : jackaraz
@contact : Jack Y. Araz <jackaraz@gmail.com>
"""

import os, logging, subprocess
from .JobControl import JobControl

"""
#!/bin/bash
#SBATCH --job-name="NAME" 
#SBATCH --mail-type=END                 # when to send mail BEGIN END FAIL REQUEUE ALL
#SBATCH --mail-user=mail address
#SBATCH --error="XXX-%j.err"
#SBATCH
#SBATCH
#SBATCH
#SBATCH
#SBATCH
"""




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
        self.just_submit = kwargs.get('just_submit',False)

        # in case one needs to source a specific python environment it can be
        # given separately 
        self.source = kwargs.get('source',[])
        if type(self.source) == str:
            self.source = [self.source]
        if type(self.source) != list:
            raise Warning('Sorce can only be a string or a list of strings.')

        if not os.path.isdir(self.log_path):
            os.mkdir(self.log_path)

        try:
            self.control   = JobControl().update_log()
        except:
            pass # check this part!!
        self.JobIDinit = 0



    def write(self,*args,**kwargs):
        if len(args) == 0:
            jobID = max([int(x.split('.sh')[0].split('_')[1]) \
                            for x in os.listdir('.') if 'jobID_' in x]+\
                            [self.JobIDinit])+1
            self.filename = 'jobID_{:03d}'.format(jobID)
        else:
            self.filename = args[0]
        file = open(self.filename+'.sh','w')
        file.write('#!/bin/sh\n')
        file.write('#SBATCH --job-name="'+self.filename+'"\n')
        if self.mail != 'mailname@durham.ac.uk':
            file.write('#SBATCH --mail-type=END\n')
            file.write('#SBATCH --mail-user='+self.mail+'\n')

        if kwargs.get('cpu',False):
            file.write('#SBATCH --partition=cpu\n')
        if kwargs.get('export',False):
            file.write('#SBATCH --export=ALL\n')

        self.run_command = kwargs.get('command',[])
        if type(self.run_command) == str:
            self.run_command = [self.run_command]
        commands = {}
        if len(self.run_command)> 0:
            single_cmd   = [x for x in self.run_command if type(x) == str]
            parallel_cmd = [x for x in self.run_command if type(x) == list]
            if len(single_cmd) > 0:
                run_command = self.core_command + single_cmd
                commands[0] = (len(parallel_cmd)>0)*'srun '+' '.join(run_command)+'\n'
            for ix, cmd in enumerate(parallel_cmd):
                run_command    = self.core_command + cmd
                commands[ix+(len(commands.keys())>0)*1] = 'srun '+' '.join(run_command)+'\n'
        else:
            commands[0] = ' '.join(self.core_command)

        file.write('#SBATCH --error="'+os.path.join(self.log_path,
                                                    self.filename+(len(commands.keys())>1)*'_%j'+'.err')+'"\n')
        file.write('#SBATCH --output="'+os.path.join(self.log_path,
                                                     self.filename+(len(commands.keys())>1)*'_%j'+'.out')+'"\n\n')
        occupied = ','.join(self.occupied_list())
        if occupied != '':
            file.write('#SBATCH --exclude='+occupied+'\n\n')
        else:
            file.write('# nothing to exclude \n\n')

        path = os.path.join(self.core_path,kwargs.get('path',''))
        file.write('cd '+path+'\n')

        # retreive source 
        if len(self.source) != 0:
            file.write('\n'.join(self.source)+'\n\n')

        for key, cmd in commands.items():
            file.write(cmd+(not cmd.endswith('\n'))*'\n')
        file.write('\n\n\nexit 0\n')
        file.close()
        return True



    def occupied_list(self):
        """
            Creates a list of the computers that are already have jobs.
            PS: if the server is overloaded, workstations will not be excluded.
        """
        job_list = subprocess.Popen('squeue', shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        job_list = job_list.stdout.read().decode('utf-8').split('\n')[1:-1]

        ls_temp = [x.split()[len(x.split())-1] for x in job_list if not '(' in x]
        myjobs  = [x.split()[len(x.split())-1] for x in job_list if not '(' in x and os.environ['LOGNAME'] in x]

        ls = []
        # os.remove('.log.txt')
        for i in ls_temp:
            if self.just_submit:
                if not i in myjobs and not i in ls:
                    ls.append(i)
            else:
                if not i in ls:
                    ls.append(i)
        if len(ls) >= 40 or self.just_submit:
            new_ls = [x for x in ls if ('ip3' not in x)]
            for elem in myjobs:
                if elem not in new_ls:
                    new_ls.append(elem)
            return new_ls
            #return [x for x in ls if not 'ip3' in x]
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

        jobID     = self._submit(filename)
        check_job = self._checkJob(jobID)

        just_submit_default = self.just_submit
        if check_job == -1:
            return
        elif check_job == 0:
            self.just_submit = True
            if self.write(filename,command=self.run_command):
                jobID     = self._submit(filename)
                check_job = self._checkJob(jobID)
                self.just_submit = just_submit_default
                if check_job == 1: 
                    print(u'\u001b[36m   * '+filename+u': submitted with another job...\u001b[0m')

        if check_job == 1:
            submit_log = open(self.submit_log,'a+')
            submit_log.write(filename+' '+jobID+'\n')
            submit_log.close()
            if remove_after_submission:
                os.remove(filename+'.sh')
                self.JobIDinit += 1
            return


    def _checkJob(self,jobID):
        cmd_check = 'squeue -u '+os.environ['LOGNAME']+' | grep '+jobID
        check_job = subprocess.Popen(cmd_check, shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        check_job = check_job.stdout.read().decode('utf-8')
        if check_job == '':
            print(u'\u001b[31m   * '+self.filename+ u': not running...\u001b[0m')
            return -1
        elif 'ReqNodeNotAvail' in check_job:
            print(u'\u001b[31m   * '+self.filename+ u': Cant find available node, cancelling...\u001b[0m')
            os.system('scancel '+jobID)
            return 0
        else:
            return 1


    def _submit(self,filename):
        cmd_submit = 'sbatch ' + filename+'.sh'
        sbatch = subprocess.Popen(cmd_submit, shell=True, 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        sbatch = sbatch.stdout.read().decode('utf-8')
        return sbatch.split()[-1]


