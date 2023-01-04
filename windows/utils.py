# MIT License

# Copyright (c) 2022 Ben.Thornton955@cranfield.ac.uk
# (ben.thornton@astrazeneca.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Miscellaneous utilities.

AUTHOR: Ben-Lukas Thornton.
DATE: Oct16-22.
LAST REVISED: OCT16-22.
Ben.Thornton955@cranfield.ac.uk, ben.thornton@astrazeneca.com

Miscellaneous command-line utilities for pretty-printing coloured
error or warning messages to the use.

! Ensure that these are only output to `sys.stderr` !

Typical usage example:
----------------------
    `warn(args.verbosity, "Superfluous input detected")`
    `error("Could not find input .vchk file")`
"""

import sys

from termcolor import colored


def warn(verbosity, message) -> None:
    """Warns the user (in yellow) of a non-critical issue in their inputs. E.g. superfluous inputs.

    Args:
        verbosity:
            `bool`. Only print to stderr if this is `True`.
        message:
            The message to print.
    """
    if verbosity:
        print(colored(f"Warning! {message}", "yellow"), file=sys.stderr)


def error(message) -> None:
    """Informs the user (in red) of a critical issue. E.g. no input file
    detected or cannot parse command-line arguments. This message will
    usually be followed by termination of the program's execution.

    Args:
        message:
            The message to print.
    """

    print(colored(f"Error: {message}", "red"), file=sys.stderr)


def write_as_text(out_dir, file_name, text) -> None:
    """Writes a singular .vchk section out to a singular .txt file.

    Takes a specified section from the input .vchk file and
    writes it to a file, without any adulterations.

    Args:
        out_dir: 
            Where to place the containing folder.
        file_name:
            The name of the newly created file.
            Typically the name of the section in
            lower-case.
        text:
            The list of lines to write to the file.
    """

    try:
        with open(f"{out_dir}/{file_name}/{file_name}.txt",
                  "w", encoding="utf-8") as file_to_write:

            for line in text:
                file_to_write.write(line)

    except IOError:
        error(f"Could not write to file {out_dir}/{file_name}.txt")
