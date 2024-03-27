

```python split_filterbanks.py --help
usage: split_filterbanks.py [-h] -i INFILE [-o OUTDIR] [-n NCHANS] [-s SPLITS] [--overlap OVERLAP] [-r RUN] [-t TYPE] [--ncpus NCPUS] [--log LOG]

A script that will split a filterbank multiple smaller files using your_writer (https://github.com/thepetabyteproject/your/). It will cut out the wanted frequency channels. Optional 50 percent
overlap between the newly created subbands. Outname will be <infile>_cl_h.fil in which l is the low channel number (including) and h is the high channel number (excluding). I.e., infile_c0_64.fil
will contain the first 64 channels (channels 0, 1, .., 63) of the original infile.fil. Output files will be placed in the same folder as the infile.

options:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        (Full) path name to the input filterbank file (default: /home/msnelders/YOURPATHNAMEHERE/infile.fil).
  -o OUTDIR, --outdir OUTDIR
                        Optional path name to directory where the output filterbanks will be written to (default: same directory as input directory
  -n NCHANS, --nchans NCHANS
                        The number of channels in the input filterbank file (default: 1536).
  -s SPLITS, --splits SPLITS
                        Comma separated string indicating how many channels the output filterbank files must have (default: 64,128,256,512).
  --overlap OVERLAP     If this is a string True, the script will also create filterbanks which have 50 percent overlap with adjacent filterbanks (default: True).
  -r RUN, --run RUN     If this is a string True, the script will run and print the commands, otherwise it will only print (default: False).
  -t TYPE, --type TYPE  Output format of the output files (fil or fits, default: fil).
  --ncpus NCPUS         Number of CPUs to use with multiprocessing default: 1).
  --log LOG             If this is a string True, your_writer.py will produce a log file (default: False).
```

