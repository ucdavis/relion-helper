import contextlib
import fileinput
import re
import os
import datetime
import glob
import sys

from rich import print as pprint

from .utils import working_dir

#backup_suffix = '.{0}.bak'.format(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M"))

help = '''
Updates a Relion project's cached GUI entries with values pulled from
the appropriate environment variables. Use when a different Relion module
was previously used for the given project.
'''

def build_opt_mapping():
    opt_mapping = {'fn_ctffind_exe':    os.getenv('RELION_CTFFIND_EXECUTABLE'),
                   'fn_gctf_exe':       os.getenv('RELION_GCTF_EXECUTABLE'),
                   'fn_motioncor2_exe': os.getenv('RELION_MOTIONCOR2_EXECUTABLE'),
                   'qsubscript':        os.getenv('RELION_QSUB_TEMPLATE')}

    for value in opt_mapping.values():
        if value is None:
            pprint(f'[bold red]${value}[/bold red] is not defined; is a relion module loaded?', file=sys.stderr)
            sys.exit(1)
    
    return opt_mapping


def build_args(parser):
    pass


def run(args):
    opt_mapping = build_opt_mapping()
    
    with working_dir(args.project_dir):
        cache_files = list(glob.glob('.gui_*job.star'))
        n_changes = 0

        with fileinput.input(files=cache_files, inplace=True, backup='.bak') as fp:
            for line in fp:
                line = line.rstrip('\n')
                tokens = re.findall(r'\s?(\s*\S+)', line)
                if tokens and tokens[0] in opt_mapping:
                    new_value = opt_mapping[tokens[0]]
                    if tokens[1].strip() != new_value:
                        if not args.quiet:
                            pprint(f'> {fileinput.filename()}:[magenta]{fileinput.filelineno()}[/magenta]\n'\
                                  f'[yellow]{tokens[1]}[/yellow] => [green]{new_value}[/green]', file=sys.stderr)
                        tokens[1] = opt_mapping[tokens[0]]
                        line = ' '.join(tokens)
                        n_changes += 1
                print(line)

        if n_changes == 0:
            print('No changes made, project configuration matches current Relion module.',
                  file=sys.stderr)

