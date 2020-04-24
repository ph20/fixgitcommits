#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Script for fast fix email and name in previous git commits
"""

import subprocess
import sys
import re
import os

GIT_BIN = '/usr/bin/git'

FILTER = """WRONG_EMAIL="{WRONG_EMAIL}"
NEW_NAME="{NEW_NAME}"
NEW_EMAIL="{NEW_EMAIL}"

if [ "$GIT_COMMITTER_EMAIL" = "$WRONG_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$NEW_NAME"
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$WRONG_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$NEW_NAME"
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi"""


def git(path, args):
    return subprocess.check_output([GIT_BIN] + args,
                                   cwd=path).decode()


def gather_emails(path):
    emails_out = git(path, ['shortlog', '--summary', '--numbered', '--email'])
    emails_list = []
    for line in emails_out.splitlines():
        email_matched = re.match(r'\s+\d+\s+([^<]*)\s+<([^>]+)+', line)
        if email_matched:
            name, email = email_matched.group(1, 2)
            emails_list.append([name, email])
    return emails_list


def fix_email(path, wrong_email, new_email, new_name):
        filter_ = FILTER.format(WRONG_EMAIL=wrong_email,
                                NEW_EMAIL=new_email,
                                NEW_NAME=new_name)
        git(path, ['filter-branch', '-f', '--env-filter',
                   filter_,
                   '--tag-name-filter', 'cat', '--', '--branches', '--tags'])


def git_config_items(path, conf):
    items_list = []
    for line in git(path, ['config', '--get-regexp', conf]).splitlines():
        conf_line, item = line.split(maxsplit=1)
        if conf_line.strip() == conf:
            items_list.append(item.strip())
    return items_list


def menu(path):
    choice_list = gather_emails(path)
    print('Please choose the email and name for corrections:')
    choice_dict = dict()
    numb = 1
    for numb, (email, name) in enumerate(choice_list, start=1):
        print('    [{}] <{}> {}'.format(numb, name, email))
        choice_dict[numb] = (name, email)

    choice_str = input("  Enter your choice [1-{}]: ".format(numb))
    choice_num = int(choice_str)
    wrong_email, wrong_name = choice_dict[choice_num]
    print('')

    print('Please enter new email for replace "{}"'.format(wrong_email))
    choice_dict = dict()
    emails_choice = [_[1] for _ in choice_list if _[1] != wrong_email] + git_config_items(path=path, conf='user.email')
    for numb, email in enumerate(emails_choice, start=1):
        print('    [{}] {}'.format(numb, email))
        choice_dict[numb] = email
    print('    [{}] Manually enter'.format(numb + 1))
    choice_str = input("  Enter your choice [1-{}]: ".format(numb + 1))
    choice_num = int(choice_str)
    if choice_num == numb + 1:
        new_email = input("New email [{}]: ".format(wrong_email))
    else:
        new_email = choice_dict[choice_num]
    print('')

    print('Please enter new name for replace "{}"'.format(wrong_name))
    choice_dict = dict()
    names_choice = [_[0] for _ in choice_list if _[0] != wrong_name] + git_config_items(path=path, conf='user.name')
    for numb, name in enumerate(names_choice, start=1):
        print('    [{}] {}'.format(numb, name))
        choice_dict[numb] = name
    print('    [{}] Manually enter'.format(numb + 1))
    choice_str = input("  Enter your choice [1-{}]: ".format(numb + 1))
    choice_num = int(choice_str)
    if choice_num == numb + 1:
        new_name = input("New name [{}]: ".format(wrong_name))
    else:
        new_name = choice_dict[choice_num]
    print('')

    accepted = input('Old name/email "{} <{}>" will be replaced with "{} <{}>"\n'
                     'This operation may break your git repository.\n'
                     'start operation (Y/N)[N]: '.format(wrong_name, wrong_email, new_name, new_email))
    if accepted == 'Y':
        fix_email(path=path, new_email=new_email, new_name=new_name, wrong_email=wrong_email)
    else:
        print('Operation stopped')


def main(argv):
    path = '.'
    if len(argv) == 1:
        path = argv[0]
    elif len(argv) == 0:
        path = os.getcwd()
    else:
        print('{} [git repository path]'.format(os.path.basename(sys.argv[0])))
        sys.exit(1)
    menu(path=path)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('\nStopped')

