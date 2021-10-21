import argparse
import os
import numpy as np
from multiprocessing import Pool

parser = argparse.ArgumentParser(description="""A script that will split a filterbank multiple smaller files using your_writer (https://github.com/thepetabyteproject/your/).
It will cut out the wanted frequency channels.
Optional 50 percent overlap between the newly created subbands.
Outname will be <infile>_cl_h.fil in which l is the low channel number (including) and h is the high channel number (excluding).
I.e., infile_c0_64.fil will contain the first 64 channels (channels 0, 1, .., 63) of the original infile.fil.
Output files will be placed in the same folder as the infile.""")
parser.add_argument(
    '-i', '--infile',
    default='/home/msnelders/YOURPATHNAMEHERE/infile.fil',
    type=str,
    help="(Full) path name to the input filterbank file (default: %(default)s).")
parser.add_argument(
    '-n', '--nchans',
    default=1536,
    type=int,
    help='The number of channels in the input filterbank file (default: %(default)d).')
parser.add_argument(
    '-s', '--splits',
    default='64,128,256,512',
    type=str,
    help='Comma separated string indicating how many channels the output filterbank files must have (default: %(default)s).')
parser.add_argument(
    '-o', '--overlap',
    default='True',
    type=str,
    help="If this is a string True, the script will also create filterbanks which have 50 percent overlap with adjacent filterbanks (default: %(default)s).")
parser.add_argument(
    '-r', '--run',
    default='False',
    type=str,
    help="If this is a string True, the script will run and print the commands, otherwise it will only print (default: %(default)s).")
parser.add_argument(
    '-t', '--type',
    default='fil',
    type=str,
    help="Output format of the output files (fil or fits, default: %(default)s).")
parser.add_argument(
    '--ncpus',
    default=1,
    type=int,
    help="Number of CPUs to use with multiprocessing default: %(default)s).")
parser.add_argument(
    '--log',
    default='False',
    type=str,
    help="If this is a string True, your_writer.py will produce a log file (default: %(default)s).")

def run_commands(cmds):
    return os.system(cmds)

def check_ints(args):
    try:
        s = [int(x) for x in args.splits.split(",")]
    except ValueError:
        print("Non-integer found in args.splits - exiting script.")
        exit()
    if not all(i >= 2 for i in s):
        print("Found invalid integer. All integers must be >= 2. - exiting script.")
        exit()


def check_division(args):
    splits = [int(x) for x in args.splits.split(",")]
    n = int(args.nchans)
    for ss in splits:
        if ss == n:
            print("Split value equels number of channels. This is would just duplicate the file. - exiting script.")
            exit()
        if not n % ss == 0:
            print("{} is not divisible by {} - exiting script".format(n, ss))
            exit()


def create_chan_nums(n, splits, overlap):
    chan_tuples = []

    if overlap == "True":
        for s in splits:
            for i in np.arange(0, n - s // 2, s // 2):
                chan_tuples.append((i, i + s))

    else:
        for s in splits:
            for i in np.arange(0, n, s):
                chan_tuples.append((i, i + s))

    return chan_tuples

def create_commands(args, path, infile, chan_splits):
    """ write docstring """
    cmds = []
    for cs in chan_splits:
        l, h = cs[0], cs[1]
        outname = infile.split(".")[0]
        outname += "_c{}_{}".format(l, h)
        if args.log == "True":
            cmd = "your_writer.py -t {} -c {} {} -o {} -name {} -f {}".\
                format(args.type, l, h, path, outname, infile)
        else:
            cmd = "your_writer.py --no_log_file -t {} -c {} {} -o {} -name {} -f {}".\
                format(args.type, l, h, path, outname, path+infile)
        cmds.append(cmd)

    return cmds


def chenk_input(args):
    check_ints(args)
    check_division(args)
    splits = [int(x) for x in args.splits.split(",")]
    n = args.nchans
    overlap = args.overlap

    infile = args.infile
    infile_base = infile.split("/")[-1]

    path = "/".join(infile.split("/")[:-1]) + "/"
    if path == "/":
        path = "./"

    chan_splits = create_chan_nums(n, splits, overlap)

    cmds = create_commands(args, path, infile_base, chan_splits)

    p = Pool(processes=args.ncpus)

    for c in cmds:
        print(c)
    print("We are going to run {} commands".format(len(cmds)))

    if args.run == "True":
        p.map(run_commands, cmds)
    else:
        print("args.run does not equal True. Just printing the commands, not excecuting them.")


if __name__ == "__main__":
    args = parser.parse_args()
    chenk_input(args)
