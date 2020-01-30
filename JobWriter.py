#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 17:13:27 2020

@author: jackaraz
contact: jackaraz@gmail.com
"""

import os

def occupied_list():
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


def JobWriter(**kwargs):
    """
        Write a job file to run
    """
    filename = kwargs.get('filename','job')
    path = kwargs.get('path','NaN')
    if not os.path.isdir(path):
        return False
    command = kwargs.get('command',[])
    if command == []:
        return False
    file = open(filename+'.sh','w')
    file.write('#!/bin/sh\n')
    file.write('#SBATCH --mail-type=ALL\n')
    file.write('#SBATCH --mail-user='+kwargs.get('mail','mailname@durham.ac.uk')+'\n')
    log_path = kwargs.get('log_path','/mt/home/jaraz/main/log/')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    file.write('#SBATCH --error="'+os.path.join(log_path,filename+'.err')+'"\n')
    file.write('#SBATCH --output="'+os.path.join(log_path,filename+'.out')+'"\n\n')
    occupied = occupied_list()
    if occupied != '':
        file.write('#SBATCH --exclude='+occupied+'\n\n')

    file.write('cd '+path+'/'+filename+'\n')
    file.write(' '.join(command)+'\n')
    file.write('exit 0\n')
    file.close()
    return True