import contextlib
import fileinput
import re
import os
import datetime
import glob
import shlex
import sys

from rich import print as pprint

from .utils import working_dir

#backup_suffix = '.{0}.bak'.format(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M"))

help = '''
Updates a Relion project's cached GUI entries with values pulled from
the appropriate environment variables. Use when a different Relion module
was previously used for the given project.
'''

def get_env(env_var, allow_undef=False):
    value = os.getenv(env_var)

    if not allow_undef and value is None:
        pprint(f'[bold red]${env_var}[/bold red] is not defined; is a relion module loaded?', file=sys.stderr)
        sys.exit(1)

    return value
    

def build_opt_mapping():
    opt_mapping = {'fn_ctffind_exe':    get_env('RELION_CTFFIND_EXECUTABLE'),
                   'fn_gctf_exe':       get_env('RELION_GCTF_EXECUTABLE'),
                   'fn_motioncor2_exe': get_env('RELION_MOTIONCOR2_EXECUTABLE'),
                   'qsubscript':        get_env('RELION_QSUB_TEMPLATE')}

    for extra in range(1,10):
        opt_mapping[f'qsub_extra{extra}'] = get_env(f'RELION_QSUB_EXTRA{extra}_DEFAULT',
                                                    allow_undef=True)

    return opt_mapping


def build_args(parser):
    pass


def print_diff_header():
    pprint(f'> {fileinput.filename()}:[magenta]{fileinput.filelineno()}[/magenta]:',
           file=sys.stderr)


def run(args):
    opt_mapping = build_opt_mapping()
    
    with working_dir(args.project_dir):
        cache_files = list(glob.glob('.gui_*job.star'))
        n_changes = 0

        with fileinput.input(files=cache_files, inplace=True, backup='.bak') as fp:
            for line in fp:
                tokens = shlex.split(line)
                cache_var_name = None if not tokens else tokens[0].strip()
                if tokens and cache_var_name in opt_mapping:
                    new_value = opt_mapping[cache_var_name]
                    old_value = tokens[1].strip()

                    if new_value is None:
                        print_diff_header()
                        pprint(f'  {cache_var_name}: [red]undefined, deleting.[/red]',
                               file=sys.stderr)
                        n_changes += 1
                        continue
                    else:
                        new_value = new_value.strip()
                        if old_value != new_value:
                            if not args.quiet:
                                print_diff_header()
                                pprint(f'  {cache_var_name}: [yellow]{old_value}[/yellow] => [green]{new_value}[/green]',
                                       file=sys.stderr)
                            tokens[1] = f'"{new_value}"'
                            line = ' '.join(tokens)
                            n_changes += 1
                print(line.rstrip())

        if n_changes == 0:
            print('No changes made, project configuration matches current Relion module.',
                  file=sys.stderr)

