import argparse

from . import subset_particles
from . import reset_cache



def build_common_args(parser):
    parser.add_argument('-p', '--project-dir', default='.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False)


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func = lambda _: parser.print_help())
    commands = parser.add_subparsers()

    reset_cache_parser = commands.add_parser('reset-cache',
                                             description=reset_cache.help)
    build_common_args(reset_cache_parser)
    reset_cache_parser.set_defaults(func=reset_cache.run)
    reset_cache.build_args(reset_cache_parser)

    subset_particles_parser = commands.add_parser('subset-particles')
    subset_particles_parser.set_defaults(func=subset_particles.run)
    subset_particles.build_args(subset_particles_parser)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
