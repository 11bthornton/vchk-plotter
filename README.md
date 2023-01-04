# VCHKPlotter Manual
VCHKPlotter version 0.314159.    Author: Ben-Lukas Thornton (Ben.Thornton955@cranfield.ac.uk), s405955

## Requirements
---
- Python >= 3.10
- A suitable install of pip
- Windows requires you to install dependencies manually.
  (Install all the packages in DEPENDENCIES.txt to a VENV)
  These are suitably referenced and cited in the report,
  where necessary.

## Installation
---
### Linux:
Inside the folder that contains setup.py, execute:
> `pip install .` 

### Windows:
No install available. See usage instructions for Windows below.

## Usage
---
For all specified output types, the program will create a subfolder
in `./output_location` with the name identical to the title of the
section in the input file. E.g. "st". Lower case. The program will always print the "sn" section to *stdout*. If this option
is passed as a command-line flag, then it will be saved additionally as a `.txt`
file in the `sn` subfolder, but there will be no graph for this section.

### Linux:
After install, to produce all plots in "verbose" mode, execute:
> `VCHKPlotter ./path_to_input.vchk ./output_location -a -v`
### Windows:
This package provides a `./windows` directory. This directory contains
a windows friendly copy of the code and can be executed by running:
> `python ./__main__.py ...args...`
### Advanced Usage Instructions:
---
- Use the `-a` flag to request all output types. Note that with use of this flag,
you can use the `-no-` variants of the file-type flags to exclude them. As opposed
to typing all the outputs you do want, sometimes it's easier to just specify those
you *don't*. 

- Use the `-v` for verbose output. Will catch superfluous arguments and print to *stderr* in yellow.
- Use the following flags to select manually the types of outputs you want: `-af`, `-dp`, `-hwe`, `-idd`, `-psc`, `-psi`, `-qual`, `-sis`, `-sn`, `-st`, `-tstv`. You can provide these in all capitals or all lower case.
- When using the `-a` flag, you can switch off certain outputs by prefixing the above arguments with `-no-`. The on and off variant of a flag are mutually exclusive. The program will *error* if you provide `-af -no-af` for example.