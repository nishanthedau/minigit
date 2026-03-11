import argparse #for parsing command line arguments
import configparser #for parsing config files
from datetime import datetime #for getting the current date and time

try:
    import grp, pwd #for getting the current user and group
except ModuleNotFoundError:
    pass

from fnmatch import fnmatch #for matching file patterns
import hashlib #for hashing files uses SHA-1 algorithm
from math import ceil #for calculating the number of chunks needed to hash a file and also for rounding up the number of chunks needed to hash a file
import os #for working with files and directories and good filesys abstraction routines
import re #for regular expressions for parsing the config file
import sys #for exiting the program with an error code
import zlib #for compressing and decompressing files using the DEFLATE algorithm

argparse = argparse.ArgumentParser(description = "A simple backup utility that uses a config file to specify which files to backup and where to store the backups.")

argsubparsers = argparse.add_subparsers(title= "Command", dest = "command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
    args = argparse.parse_args(argv)
    match args.command:
        case "add": cmd_add(args)
        case "cat-file": cmd_cat_file(args)
        case "check-ignore": cmd_check_ignore(args)
        case "checkout": cmd_checkout(args)
        case "commit": cmd_commit(args)
        case "hash-object": cmd_hash_object(args)
        case "init": cmd_init(args)
        case "log": cmd_log(args)
        case "ls-files": cmd_ls_files(args)
        case "ls-tree": cmd_ls_tree(args)
        case "rev-parse": cmd_rev_parse(args)
        case "rm": cmd_rm(args)
        case "show-ref": cmd_show_ref(args)
        case "status": cmd_status(args)
        case "tag": cmd_tag(args)
        case _:print("error : bad command")
        
