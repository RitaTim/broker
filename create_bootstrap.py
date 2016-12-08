import virtualenv

PYTHON_VERSION = '2.7'

BOOTSTRAP_EXTRA = """
import os, sys

prj_dir = os.path.dirname(os.path.abspath(__file__))
prj_name = os.path.split(prj_dir)[-1]
env_dir = os.path.normpath(os.path.join(prj_dir, '..', prj_dir + '-env'))

MANAGE_SCRIPT = \"\"\"
#!{{python}}

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
\"\"\".strip()

def adjust_options(options, args):
    #options.search_dirs.insert(0, os.path.join(prj_dir, 'vendor', 'packages'))
    #options.never_download = True
    options.use_distribute = True
    options.system_site_packages = True
    args.append(env_dir)

def after_install(options, home_dir):

    join = os.path.join
    if sys.platform != 'win32':
        _path = join(home_dir, 'lib', 'python{python_version}',
                     'site-packages', 'project.pth')
    else:
        _path = join(home_dir, 'Lib', 'site-packages', 
                     'project.pth')
    with open(_path, 'w') as pth_file:
        for dir in ('modules', 'conf'):
            pth_file.write(join(prj_dir, dir) + '\\n')
    bin = 'bin' if sys.platform != 'win32' else 'Scripts'
    manage_fname = join(home_dir, bin, 'manage')
    with open(manage_fname, 'w') as manage_file:
        manage_file.write(MANAGE_SCRIPT.format(python=join(home_dir, bin,
                                                           'python' if sys.platform != 'win32' else 'python.exe')))
    os.chmod(manage_fname, 0755)

    if sys.platform != 'win32':
        bindir = join(prj_dir, 'bin')
        if not os.path.exists(bindir):
            if os.path.islink(bindir):
                os.unlink(bindir)
            os.symlink(join(home_dir, 'bin'), bindir)
    else:
        print 'Warning! This project is not intended to run in Win32 environment.'
""".strip()

output = virtualenv.create_bootstrap_script(
    BOOTSTRAP_EXTRA.format(python_version=PYTHON_VERSION),
    python_version=PYTHON_VERSION)

open('bootstrap.py', 'w').write(output)
