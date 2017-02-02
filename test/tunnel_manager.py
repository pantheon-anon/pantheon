#!/usr/bin/env python

import os
import sys
import signal
import subprocess
from subprocess import Popen, PIPE, check_output


def destroy(procs):
    # send SIGTERM signal to all processes and the subprocesses they spawned
    for proc in procs.itervalues():
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def main():
    procs = {}  # manage tunnel processes
    prompt = ''
    sys.stdout.write('tunnel manager is running\n')
    sys.stdout.flush()

    while True:
        raw_cmd = sys.stdin.readline().strip()
        # print all commands fed to tunnel manager
        sys.stderr.write(prompt + raw_cmd + '\n')
        cmd = raw_cmd.split()

        # manage I/O of multiple tunnels
        if cmd[0] == 'tunnel':
            if len(cmd) < 3:
                sys.stderr.write('error: usage: tunnel ID CMD...\n')
                continue

            try:
                tun_id = int(cmd[1]) - 1
            except:
                sys.stderr.write('error: usage: tunnel ID CMD...\n')
                continue

            cmd_to_run = ' '.join(cmd[2:])

            if cmd[2] == 'mm-tunnelclient' or cmd[2] == 'mm-tunnelserver':
                # expand $MAHIMAHI_BASE
                cmd_to_run = os.path.expandvars(cmd_to_run).split()
                procs[tun_id] = Popen(cmd_to_run, stdin=PIPE, stdout=PIPE,
                                      preexec_fn=os.setsid)
            elif cmd[2] == 'python':  # run python scripts inside tunnel
                procs[tun_id].stdin.write(cmd_to_run + '\n')
            elif cmd[2] == 'readline':  # readline from stdout of tunnel
                if len(cmd) != 3:
                    sys.stderr.write('error: usage: tunnel ID readline\n')
                    continue

                sys.stdout.write(procs[tun_id].stdout.readline())
                sys.stdout.flush()
            else:
                sys.stderr.write('unknown command after "tunnel ID": %s\n'
                                 % cmd_to_run)
                continue
        elif cmd[0] == 'prompt':  # set prompt in front of commands to print
            if len(cmd) != 2:
                sys.stderr.write('error: usage: prompt PROMPT\n')
                continue

            prompt = cmd[1].strip() + ' '
        elif cmd[0] == 'halt':  # terminate all tunnel processes and quit
            if len(cmd) != 1:
                sys.stderr.write('error: usage: halt\n')
                continue

            destroy(procs)
            sys.exit(0)
        else:
            sys.stderr.write('unknown command: %s\n' % raw_cmd)
            continue


if __name__ == '__main__':
    main()
