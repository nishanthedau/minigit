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
        
class GitRepository(object):
    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository {path}")
        
        self.conf = configparser.ConfigParser()
        cf = self.repo_file(self, "config")

        if cf and os.path.exists(cf): # Check if config file exists
            self.conf.read(cf)
        elif not force:
            raise Exception(f"Config file's missing {cf}")
        
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion: {vers}")
            
def repo_path(repo, *path):
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

def repo_dir(repo, *path, mkdir=False):
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None
    
def repo_create(path):
    repo = GitRepository(path, True)

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception (f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception (f"{path} is not empty!")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo

def repo_default_config():
    ret = configparser.ConfigParser()
    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret

argsp = argsubparsers.add_parser("init", help ="Initialize a new, empty repository.")

argsp.add_arguement("path", 
                    metavar="directory", 
                    nargs="?", 
                    default=".", 
                    help="Where to create the repository.")

def cmd_init(args):
    repo_create(args.path)