# Copyright (C) 2014 Jonathon Ogden   < jeog.dev@gmail.com >
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License,
#   'LICENSE.txt', along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.

from tosdb import *
from tosdb import _SYS_IS_WIN, _Thread

from argparse import ArgumentParser as _ArgumentParser
from sys import stderr as _stderr
from time import sleep as _sleep

args=None
            
def _main_init():
    global args
    parser = _ArgumentParser()
    parser.add_argument('--virtual-client', type=str,
                        help='initialize virtual client "address port [timeout]"')
    parser.add_argument('--virtual-server', type=str,
                        help='start virtual server "address port [timeout]"')
    parser.add_argument('--root', help='root directory to search for the library')
    parser.add_argument('--path', help='the exact path of the library')
    parser.add_argument('--auth', help='password to use for authentication')
    parser.add_argument('-v', '--verbose', action="store_true", 
                        help='extra info to stdout about client connection(s)')
    args = parser.parse_args()  

    #remove quotes 
    if args.auth:
        args.auth = args.auth.strip("'").strip('"')
        
    if args.virtual_server and _SYS_IS_WIN:
        raw_args = args.virtual_server.split(' ')
        try:
            vs_args = ((raw_args[0],int(raw_args[1])),)
        except IndexError:
            print("usage: tosdb --virtual-server 'address port [timeout]'",file=_stderr)
            exit(1)
        vs_args += (args.auth,)
        vs_args += (int(raw_args[2]),) if len(raw_args) > 2 else (DEF_TIMEOUT,) 
        vs_args += (args.verbose,)
        #spin off so we don't block on exit
        _Thread(target=enable_virtualization,args=vs_args).start()
      
    if args.virtual_client:
        raw_args = args.virtual_client.split(' ')
        try:
            vc_args = ((raw_args[0],int(raw_args[1])),)
        except IndexError:
            print("usage: tosdb --virtual-client 'address port [timeout]'",file=_stderr)
            exit(1)
        vc_args += (args.auth,)
        vc_args += (int(raw_args[2]),) if len(raw_args) > 2 else (DEF_TIMEOUT,)      
        admin_init(*vc_args)
            
    if args.virtual_client:
        if args.path:
            vinit(dllpath=args.path)
        elif args.root:
            vinit(root=args.root)
    else:
        if args.path:
            init(dllpath=args.path)   
        elif args.root:  
            init(root=args.root)


_main_init()
globals().pop('_main_init')

if args and args.virtual_server and _SYS_IS_WIN:        
    exit_commands = ('q','Q','quit','QUIT','Quit','Exit','EXIT','exit')
    print('\n', str(exit_commands) + " to terminate\n")
    while input() not in exit_commands: 
        pass 
else:
    import code
    code.interact(local=locals())


