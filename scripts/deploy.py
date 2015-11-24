#!/usr/bin/env python3
"""Script that deploys some files (typically documentation and/or coverage
reports) to some directory
"""

import configparser
import os
import pathlib
import shutil
import sys


def parse(argv=None):
    import argparse as ap

    msg = """Deploy the documentation or coverage report to some directory,
          removing first the content of the said direcretory. The target
          directory for the deployment must be given in the ``type`` option of
          the ``[name]`` section of the ``~/.config/tox_deploy.cfg``
          configuration file. If the file, section or option do not exist, the
          deployment is aborted"""
    p = ap.ArgumentParser(usage=msg,
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)

    p.add_argument("project", help='''Name of the project. It can be replaced in
                   the target directory using the {project} placeholder
                   (without the trailing ``$``).''')
    p.add_argument('type', help='''Type of the files to deploy.  It can be
                   replaced in the target directory using the {type_}
                   placeholder (without the trailing ``$``).''')
    p.add_argument('deploy_from', help='''Directory from which to copy the
                   files''')

    return p.parse_args(args=argv)


def main(argv=None):
    args = parse(argv=argv)

    conf = configparser.ConfigParser()
    if not conf.read(os.path.join(os.path.expanduser('~'), '.config',
                     "tox_deploy.cfg")):
        print('Missing configuration file: deployment aborted')
        exit()

    try:
        deploy_to = pathlib.Path(conf[args.project][args.type]
                                 .format(name=args.project,
                                         type_=args.type))
    except KeyError:
        print('Missing section or option: deployment aborted')
        exit()

    if not deploy_to.exists():
        # do nothing
        pass
    elif deploy_to.is_dir():
        # remove the directory
        shutil.rmtree(str(deploy_to))
    else:
        print("the target is not a directory")
        sys.exit()

    # copy the content of ``args.deploy_from`` into the ``deploy_to`` directory
    shutil.copytree(args.deploy_from, str(deploy_to))

    print("Deployed")


if __name__ == "__main__":
    main()
