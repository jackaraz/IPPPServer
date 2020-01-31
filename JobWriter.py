#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:13:27 2020

@author  : jackaraz
@contact : Jack Y. Araz <jackaraz@gmail.com>
"""

import os

class JobWriter:
    def __init__(self,path,core_command, **kwargs):
        """
            Configure initial job writer
        """
        if not os.path.isdir(path):
            print('Hmm can not find '+path)
        self.core_path = path
        # path where the initial code to be run lives
        if type(core_command) == str:
            self.core_command = [core_command]
        elif type(core_command) == list:
            self.core_command = core_command
        # core command which is same for all iterations of the job
        self.mail = kwargs.get('mail','mailname@durham.ac.uk')
        self.log  = kwargs.get('log',os.path.join(os.path.expanduser('~').replace('home','batch'),
                                                  'LOG'))
        if not os.path.isdir(self.log):
            os.mkdir(self.log)

    def write(self,filename,**kwargs):
        self.filename = filename
        file = open(filename+'.sh','w')
        file.write('#!/bin/sh\n')
        if self.mail != 'mailname@durham.ac.uk':
            file.write('#SBATCH --mail-type=ALL\n')
            file.write('#SBATCH --mail-user='+self.mail+'\n')
        file.write('#SBATCH --error="'+os.path.join(self.log,filename+'.err')+'"\n')
        file.write('#SBATCH --output="'+os.path.join(self.log,filename+'.out')+'\n\n')
        occupied = self.occupied_list()
        if occupied != '':
            file.write('#SBATCH --exclude='+occupied+'\n\n')

        path = os.path.join(self.core_path,kwargs.get('path',''))
        file.write('cd '+path+'\n')
        run_command =  kwargs.get('command',[])
        if type(run_command) == str:
            run_command = [run_command]
        run_command = self.core_command + run_command
        file.write(' '.join(run_command)+'\n')
        file.write('exit 0\n')
        file.close()

    def occupied_list(self):
        """
            Creates a list of the computers that are already have jobs.
            PS: if the server is overloaded, workstations will not be excluded.
        """
        os.system('squeue > log.txt')
        with open('log.txt','r') as f:
            ls = f.readlines()
        ls = ls[1:len(ls)]
        ls_temp = [x.split()[len(x.split())-1] for x in ls if not '(' in x]
        ls = []
        os.system('rm log.txt')
        for i in ls_temp:
            if not i in ls:
                ls.append(i)
        if len(ls) >= 40:
            ls = [x for x in ls if 'ip3-ws' not in x]
        txt = ','.join(ls)
        return txt

    def Submit(self):
        os.system('sbach '+self.filename+'.sh > temp.txt')
        with open('temp.txt','r') as f:
            temp = f.readlines()
        temp = temp[0].split()[len(temp[0].split())-1]
        submit_log = open('submit.log','a+')
        submit_log.write(self.filename+' '+temp+'\n')
        submit_log.close()
        os.system('rm temp.txt')