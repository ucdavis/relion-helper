import argparse
import sys

from rich.console import Console
import starfile


def build_args(parser):
    parser.add_argument('-s', '--source-star', required=True)
    parser.add_argument('-t', '--target-star', required=True)
    parser.add_argument('-o', '--output-star', default='/sys/stdout')
    parser.add_argument('--on', default='rlnImageName')
    parser.add_argument('--particles-only', action='store_true', default=False)


def run(args):
    err = Console(stderr=True)

    err.print(f'Loading {args.source_star}...')
    src_star = starfile.read(args.source_star, always_dict=True)
    try:
        src_df = src_star['particles']
    except KeyError:
        err.print(f'{args.source_star} does not contain a "particles" block, exiting.')
        sys.exit(1)

    err.print(f'Loading {args.target_star}...')
    target_star = starfile.read(args.target_star)
    try:
        target_df = target_star['particles']
    except KeyError:
        err.print(f'{args.target_star} does not contain a "particles" block, exiting.')
        sys.exit(1)   

    err.print('Subsetting target star file...')
    try:
        src_on = src_df[args.on]
    except KeyError:
        err.print(f'{args.source_star} has no field named "{args.on}"')
        sys.exit(2)

    try:
        subset_df = target_df[target_df[args.on].isin(src_on)]
    except KeyError:
        err.print(f'{args.target_star} has no field named "{args.on}"')
        sys.exit(2)
    finally:
        subset_df.name = 'particles'

    err.print(f'Writing results to {args.output_star}...')
    if args.particles_only:
        starfile.write(subset_df, args.output_star)
    else:
        target_star['particles'] = subset_df
        starfile.write(target_star, args.output_star)

