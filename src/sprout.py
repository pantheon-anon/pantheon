#!/usr/bin/env python

import os
import sys
import usage
from subprocess import call, check_call, CalledProcessError


def main():
    usage.check_args(sys.argv, os.path.basename(__file__), 'receiver_first')
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(
        os.path.join(src_dir, '../third_party/sprout'))
    src_file = os.path.join(submodule_dir, 'src/examples/sproutbt2')

    # build dependencies
    if option == 'deps':
        deps_list = ('libboost-math-dev libssl-dev '
                     'libprotobuf-dev protobuf-compiler libncurses5-dev')
        print deps_list

    # build
    if option == 'build':
        # apply patch to reduce MTU size
        patch = os.path.join(src_dir, 'sprout_mtu.patch')
        cmd = 'cd %s && git apply %s' % (submodule_dir, patch)
        try:
            check_call(cmd, shell=True)
        except CalledProcessError:
            sys.stderr.write('patch apply failed but assuming things okay '
                             '(patch applied previously?)\n')

        # make alone sufficient if autogen.sh and configure already run
        cmd = 'cd %s && make -j4' % submodule_dir
        if call(cmd, shell=True) is not 0:
            cmd = ('cd %s && ./autogen.sh && ./configure --enable-examples && '
                   'make -j4' % submodule_dir)
            check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'init':
        pass

    # who goes first
    if option == 'who_goes_first':
        print 'Receiver first'

    # friendly name
    if option == 'friendly_name':
        print 'Sprout'

    # receiver
    if option == 'receiver':
        os.environ['SPROUT_MODEL_IN'] = os.path.join(
            submodule_dir, 'src/examples/sprout.model')
        # sproutbt2 prints the 'listening on port' message to stdout
        cmd = [src_file]
        check_call(cmd)

    # sender
    if option == 'sender':
        os.environ['SPROUT_MODEL_IN'] = os.path.join(
            submodule_dir, 'src/examples/sprout.model')
        ip = sys.argv[2]
        port = sys.argv[3]
        cmd = [src_file, ip, port]
        check_call(cmd)


if __name__ == '__main__':
    main()
