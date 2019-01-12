#!/usr/bin/env python
from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
from nipype.interfaces import fsl

from glob import glob
import time
import argparse

def init_example_wf(name='map-wf'):
    # define a workflow
    wf = pe.Workflow(name=name)

    # fetch all T1s
    inputnode = pe.Node(niu.IdentityInterface(['in_file']), name='inputnode')
    T1_images = sorted(glob('/home/neuro/ds000001/sub-*/*/*T1w.nii.gz'))
    inputnode.iterables = ('in_file', T1_images)

    # run bet for each image
    bet = pe.Node(fsl.BET(), name='bet')
    wf.connect(inputnode, 'in_file', bet, 'in_file')

    return wf

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--plugin', default='Linear',
                        help="Nipype execution plugin")
    parser.add_argument('--plugin-args', help="Nipype plugin args")
    return parser

def main():
    time0 = time.time()
    parser = get_args()
    args = parser.parse_args()

    wf = init_example_wf()
    wf.run(plugin=args.plugin, plugin_args=args.plugin_args)

    print("\nWorkflow duration:", time.time() - time0)
    return wf

if __name__ == '__main__':
    main()
