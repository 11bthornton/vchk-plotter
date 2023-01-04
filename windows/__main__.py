# MIT License

# Copyright (c) 2022 Ben.Thornton955@cranfield.ac.uk (ben.thornton@astrazeneca.com)

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
"""Main script for program.

Ben.Thornton955@cranfield.ac.uk, ben.thornton@astrazeneca.com
"""

import os
import sys

from argument_parser import CustomArgumentParser
from file_handler import FileHandler
from utils import error, warn


def main() -> None:
    """Parses command line arguments, plots the graphs, saves
    sections to text file and prints the summary numbers section
    to stdout."""

    # Use custom parser to parse the command line arguments
    # and extract the list of graphs / text files (`actions`).
    parser = CustomArgumentParser()
    args, actions = parser.parse_args()
    # actions.append("sn")

    # Tell my FileHandler instance to only bother
    # parsing the required sections. Saves (a bit of)
    # computation.
    handler = FileHandler(args, actions)
    sections = handler.parse()

    # Can only make directory and subdirectory simultaneously
    # if out_dir string ends with "/"
    if not args.out_dir.endswith("/"):
        args.out_dir = args.out_dir + "/"

    # Try and make the output folder:
    if not os.path.isdir(args.out_dir):
        try:
            os.makedirs(args.out_dir)
        except IOError:
            error("Could not create parent output folder. Exiting")
            sys.exit(1)
    else:
        warn(args.verbose,
             "Output folder already exists, program will overwrite.")

    # Now we can loop through all the things the
    # user wants and output this to the correct place...
    for action in actions:

        if not os.path.isdir(f"{args.out_dir}/{action}"):
            try:
                os.mkdir(f"{args.out_dir}/{action}")
            except IOError:
                error(
                    "Could not create subfolder. Continuing to next section.")
                # Only continue, so rest of the output still has a chance of
                # being written.

                continue

        section = sections.get_section(action)
        section.plot_and_write_file(args.out_dir)

    # Regardless of the -SN option. Print the summary numbers to stdout.
    for line in sections.get_section("sn").get_text():
        # The raw text contains the line-endings anyway.
        print(line, end="")


# Entry point to program
if __name__ == "__main__":
    main()
