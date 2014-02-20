#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: autoindent expandtab tabstop=4 sw=4 sts=4 filetype=python

"""Autotest tool - Minimalistic Continuous Integration for git"""

# Copyright (c) 2012, Adfinis SyGroup AG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Adfinis SyGroup AG nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS";
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Adfinis SyGroup AG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import os.path
import subprocess
import sys
import re
import smtplib
import argparse
from email.utils import formatdate
from email.mime.text import MIMEText

settings = {
    "project_path"    : "/home/path/go/project",
    "last_success"    : None,
    "last_test"       : None,
    "name"            : "project-master",
    "branch"          : "master",
    "smtp"            : "smtp.host.ch",
    "test_command"    : [
        "run_tests",
    ],
    "authors_command"  : [
        "git shortlog -e -s %(last_success)s...HEAD"
    ],
    "switch_command"  : [
        "bash",
        "-c",
        # If you use vagrant do not add -x because it will remove .vagrant dir
        "git clean -df; git checkout .; git checkout origin/%(branch)s"
    ],
    "pull_command"    : [
        "bash",
        "-c",
        "git fetch; git reset --hard origin/%(branch)s"
    ],
    "revision_command": [
        "bash",
        "-c",
        "git rev-parse HEAD"
    ]
}

settings_file = None
quiet         = False


class helpAction(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        parser.print_help()
        print("""
Typical setup:
# autotest -s path/to/settings.json init
# vi path/to/settings.json
# autotest -spath/to/settings.json test
        """)
        parser.exit()


def main():
    global settings_file
    global quiet
    parser = argparse.ArgumentParser(
        description="""
Autotest tool - Minimalistic Continuous Integration for git
""",
        add_help=False
    )
    parser.add_argument(
        "command",
        help="command to execute",
        choices=['init', 'test']
    )
    parser.add_argument(
        "-s",
        "--settings",
        nargs="?",
        help="Path to settings (json)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Do not output commands",
        action="store_true"
    )
    parser.add_argument(
        "-h",
        "--help",
        nargs=0,
        help="print this message and exit",
        action=helpAction
    )
    args = parser.parse_args()
    settings_file = args.settings
    quiet         = args.quiet

    if args.command == "init":
        write_settings()
    elif args.command == "test":
        execute()


def execute():
    """Executes the defined commands and sends a notification on failure."""
    read_settings()
    os.chdir(settings['project_path'])
    branch = settings["branch"]
    execute_and_print("switch_command", env={'branch' : branch})
    execute_and_print("pull_command", env={'branch' : branch})
    (
        ret,
        stdout,
        stderr
    ) = execute_external(settings["revision_command"])
    if not quiet:
        print(stdout)
        print(stderr)
    current_revision = stdout.strip()
    if settings['last_success'] is None:
        last_success = "%s^" % current_revision
    else:
        last_success = settings['last_success']
    if settings['last_test'] != current_revision:
        settings['last_test'] = current_revision
        (
            ret,
            stdout,
            stderr
        ) = execute_external(settings['test_command'])
        if not quiet:
            print(stdout)
            print(stderr)
        if ret == 0:
            settings['last_success'] = current_revision
        else:
            notify_failure(last_success, current_revision, stdout, stderr)
        write_settings()


def notify_failure(last_success, current_revision, stdout, stderr):
    """Sends a notification to all authors.

    last_success     : commit id of the last success
    current_revision : commit id of the current revision
    stdout           : of the test
    stderr           : of the test"""
    (
        ret,
        astdout,
        astderr
    ) = execute_external(
        bless_command(
            settings["authors_command"],
            locals()
        )
    )
    if not quiet:
        print(astdout)
        print(astderr)

    email_regex = re.compile("<(\S+@\S+\.\S+)>")
    emails = []
    for line in astdout.split('\n'):
        m = email_regex.search(line)
        if m:
            emails += [m.groups()[0]]
    if not quiet:
        print(emails)
    name = settings['name']
    branch = settings['branch']
    emails_string = "\n".join(emails)
    msg = """Hello there

You helped b0rking: %(name)s. Following people also commited on %(branch)s:

%(emails_string)s

Last success     : %(last_success)s
Current revision : %(current_revision)s
Bisect           : git bisect start %(current_revision)s %(last_success)s

STDERR:

%(stderr)s

STDOUT:

%(stdout)s

Best,
    Your Python
""" % {
        'name'             : name,
        'branch'           : branch,
        'emails_string'    : emails_string,
        'last_success'     : last_success,
        'current_revision' : current_revision,
        'stderr'           : stderr,
        'stdout'           : stdout
    }

    host = settings['smtp']
    sender = "autotest@%s" % host
    s = smtplib.SMTP(host)

    for email in emails:
        if not quiet:
            print("Sending email to: %s" % email)
        coded = MIMEText(msg.encode('utf-8'), _charset='utf-8')
        coded['Subject'] = "Autotest %s" % name
        coded['From'] = sender
        coded['To'] = email
        coded['Date'] = formatdate()
        s.sendmail(sender, email, coded.as_string())
    s.quit()


def bless_command(cmd, env):
    """Format the commands using the variables in env"""
    newcmd = list(cmd)
    for idx, val in enumerate(newcmd):
        newcmd[idx] = val % env
    return newcmd


def execute_and_print(cmd, env={}, communicate=True):
    """Executes and prints a command
    cmd         : the command
    env         : environment for bless
    communicate : set to False if the command forks to background
    """
    newcmd = bless_command(settings[cmd], env)
    (
        ret,
        stdout,
        stderr
    ) = execute_external(newcmd, communicate=communicate)
    if communicate:
        if not quiet:
            print(stdout)
            print(stderr)


def read_settings():
    """Read settings"""
    global settings
    if os.path.isfile(settings_file):
        f = open(settings_file, "r")
        settings = json.load(f)
        f.close()
    else:
        print("Settings not found.")
        sys.exit(1)


def write_settings():
    """Write settings"""
    f = open(settings_file, "w")
    json.dump(
        settings,
        f,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    )
    f.close()


def execute_external(command, stdin='', communicate=True):
    """Executes the given command (which should be a list).

    If you pass stdin, it will be written to the command's stdin.

    Returns a tuple of (returncode, stdout, stderr) upon completion.
    """

    # run process
    returncode = 0
    if not quiet:
        print(command, communicate)
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if communicate:
        (stdout, stderr) = proc.communicate(stdin)
        returncode = proc.wait()
        return (returncode, stdout.decode('utf8'), stderr.decode('utf8'))
    return (None, None, None)

if __name__ == "__main__":
    main()
