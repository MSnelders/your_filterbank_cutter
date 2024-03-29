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
    required = True,
    help="(Full) path name to the input filterbank file (default: %(default)s).")
parser.add_argument(
    '-o', '--outdir',
    type=str,
    required = False,
    help="Optional path name to directory where the output filterbanks will be written to (default: same directory as input directory",
    default="./")
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
    '--overlap',
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
    """ Checks if the split(s) from the input argument is/are a divisor of the number of input channels
    exist program is this is not the case """
    splits = [int(x) for x in args.splits.split(",")]
    n = int(args.nchans)
    for ss in splits:
        if ss == n:
            print("Split value equels number of channels. This is would just duplicate the file. - exiting script.")
            exit()
        if not n % ss == 0:
            print(f"{n} is not divisible by {ss} - exiting script")
            exit()


def create_chan_nums(n, splits, overlap):
    """ Creates tuples for an input number of channels n, a list of integers to split it by
    and a boolean to account for overlap.
    
    Example: n=128, splits=[64], overlap=True
    return [(0, 64), (32, 96), (64, 128)]
    Example: n=64, splits=[16,32], overlap=False
    return [(0, 16), (16, 32), (32, 48), (48, 64), (0, 32), (32, 64)]"""

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

def get_max_tup_value(t):
    """ Assumes a list of tuples in the form:
    [(0, 16), (16, 32), (32, 48), (48, 64), (0, 32), (32, 64)]
    i.e. n elements with every element a tuple with (low, high) """
    return max(max(t))

def get_number_of_digits(v):
    return len(str(v))


def create_commands(args, outpath, infile, chan_splits):
    """ Given the input paramaters of the program, write the commands for your_writer.py """
    
    # determine largest value in list of tuples
    max_tup_value = get_max_tup_value(chan_splits)
    
    # determine length of that digit
    max_len = get_number_of_digits(max_tup_value)
    
    cmds = []
    for cs in chan_splits:
        l, h = cs[0], cs[1]

        # if input file has a .fil or .fits extension, remove it from the outname. 
        if infile[-5:] == ".fits":
            outname = infile[:-5]
        elif infile[-4:] == ".fil":
            outname = infile[:-4]
        else:
            outname = infile

        # remove any potential full path names to the outname, since your_writer uses -o </path/to/dir> anyway
        outname = outname.split("/")[-1]

    
        # add channel numbers to the outname
        # pad them with leading zeros
        # e.g. fill add _c00_64 
        outname += f"_c{str(l).zfill(max_len)}_{str(h).zfill(max_len)}"

        cmd = f"your_writer.py --no_log_file -t {args.type} -c {l} {h} -o {outpath} -name {outname} -f {infile}"

        if not (args.log == "True"):
            cmd = cmd.replace("your_writer.py ", "your_writer.py --no_log_file ")

        cmds.append(cmd)

    return cmds


def chenk_input(args):
    """ To do: write docstring """
    check_ints(args)
    check_division(args)
    splits = [int(x) for x in args.splits.split(",")]
    n = args.nchans
    overlap = args.overlap

    outdir = args.outdir
    
    infile = args.infile

    if ((type(outdir) == str) & (len(outdir) >= 2)):
        outpath =  "/".join(outdir.split("/")) 
    else:
        outpath = "/".join(infile.split("/")[:-1]) + "/"

    if outpath == "/":
        outpath = "./"

    chan_splits = create_chan_nums(n, splits, overlap)

    cmds = create_commands(args, outpath, infile, chan_splits)

    p = Pool(processes=args.ncpus)

    for c in cmds:
        print(c)
    print(f"We are going to run {len(cmds)} commands")

    if args.run == "True":
        p.map(run_commands, cmds)
    else:
        print("args.run does not equal True. Just printing the commands, not excecuting them.")


if __name__ == "__main__":
    args = parser.parse_args()
    chenk_input(args)
