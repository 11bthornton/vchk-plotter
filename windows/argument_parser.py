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
"""
Custom Argument Parser Utilities.

AUTHOR: Ben-Lukas Thornton.
DATE: Oct16-22.
LAST REVISED: OCT16-22.
Ben.Thornton955@cranfield.ac.uk, ben.thornton@astrazeneca.com

Classes:
    CustomArgumentParser(argparse.ArgumentParse)
"""

import argparse

from typing import List, Tuple

from utils import error, warn


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom `argparse.ArgumentParser`.

    A custom `argparse.ArgumentParser` extended to facilitate the extraction
    of the required actions for program execution and enhance error &
    warning output for the end-user.

    ---

    Attributes
    ----------
    actions : List[str]
        a list of all actions / graphs / text files the program should
        produce on execution.
    description: str
        a helpful description of the program that is displayed when the
        `-h` help option is selected.
    """

    # List of possible command-line options: [(argument-identifer, help-text)]
    AVAILABLE_STANDALONE_ARGUMENTS = [
        ("TSTV",
         "makes a text file and graph for the transitions/transversions sections"
         ),
        ("SiS", "makes a text file and graph for the singleton stats section"),
        ("AF",
         "makes a text file and graph for the stats by non-reference allele frequency section"
         ),
        ("QUAL",
         "makes a text file and graph for the stats by quality section"),
        ("IDD",
         "makes a text file and graph for the InDel distribution section"),
        ("ST",
         "makes a text file and graph for the substitution types section"),
        ("DP",
         "makes a text file and graph for the depth distribution section"),
        ("PSC",
         "makes a text file and graph for the per-sample counts section"),
        ("PSI",
         "makes a text file and graph for the per-sample InDels section"),
        ("HWE",
         "makes a text file and graph for the Hardy Weinberg equilibrium section"),
        ("SN",
         "makes a text file and graph for the Summary Numbers section")
    ]

    def __init__(self, **kwargs) -> None:
        """Initialises the super class as usual, but forces the instance to read the
        description from the package's README. Instance variables are set to default
        values and all required arguments are then added to this instance.

        Calls the private `._construct()` method that registers each argument with the
        superclass.
        """

        super().__init__(**kwargs)
        self.description = """A tool to plot sections from a .vchk file 
            and saves their contents to disk."""

        self.actions = []

        self._construct()

    def parse_args(self, *args, **kwargs) -> Tuple[argparse.Namespace, List[str]]:
        """Calls the `.parse_args()` method on the super class and then
        performs some quality-of-life checks on the user's inputs.

        Returns
        -------
            `args, self.actions`:
                A tuple of the arguments and the extracted actions for the
                program's execution.
        """

        # Parse the command-line arguments using the inherited `.parse_args()`
        # methods.
        args = super().parse_args()
        self.actions = self._sanity_check_arguments(args)

        return args, self.actions

    def _construct(self) -> None:
        """Adds all arguments from the list of available arguments and additional
        quality-of-life arguments.

        Each `action` (see Self.AVAILABLE_STANDALONE_ARGUMENTS) can either be
        opted into, or opted out of (by prefixing the flag with `--no-`). Note that
        these are **mutually exclusive** arguments and cannot be used in conjunction
        with one another. This will cause the parser to error and exit.
        """

        # Input / output directory arguments
        self.add_argument("in_dir",
                          help="location of directory for input data")
        self.add_argument(
            "out_dir",
            help="location of output directory (or where newly created directory should be placed)"
        )

        for available_argument in CustomArgumentParser.AVAILABLE_STANDALONE_ARGUMENTS:

            # Mutually exclusive group prevents users from providing conflicting arguments.
            # Errors here are handled through inheritance.
            mutually_exclusive_group = self.add_mutually_exclusive_group()

            # Add both upper and lower case command-line flags. Nicer for the user.
            mutually_exclusive_group.add_argument(
                "-" + available_argument[0],
                "-" + available_argument[0].lower(),
                action="store_true",
                default=None,
                help=available_argument[1])
            mutually_exclusive_group.add_argument(
                "-no-" + available_argument[0],
                "-no-" + available_argument[0].lower(),
                action="store_false",
                dest=available_argument[0])

        # Additional ergonomic, quality-of-life arguments
        self.add_argument("--ALL", "-a", action="store_true")
        self.add_argument("--verbose", "-v", action="store_true")

    def error(self, message):
        """Custom error method for pretty-printing with colour.

        Overrides `argparse.ArgumentParsers`' `.error()` method to make use of this
        package's custom error message displaying capabilities. Then exits with
        non-zero exit-status.

        Args:
            message:
                The error message to display. 
        """

        error(message)
        self.exit(1)

    def _sanity_check_arguments(
            self, args_namespace: argparse.Namespace) -> List[str]:
        """Checks for superfluous or inadvertantly nonsensical inputs.

        These inputs will *not* cause the program to raise an exception, but if verbose mode is opted into
        the following conditions will be alerted to the user:
        - The user has selected the --ALL (-a) flag but also passed the flag for individual actions
            (e.g. -a --SN). (-SN is included within -a so there is little point to include the flag)
        - The user has selected no actions. The program will run to completion, but do nothing.

        Returns
            `actions`:
                The list of text files/graphs this program should
                generate.
        """

        args_dictionary = args_namespace.__dict__
        if args_namespace.ALL:

            if any(args_dictionary[arg[0]] for arg in
                   CustomArgumentParser.AVAILABLE_STANDALONE_ARGUMENTS):
                warn(
                    args_namespace.verbose,
                    "Unnecessary flag inclusion whilst --ALL flag set to true."
                )

            # Will set True & unspecified (None) arguments to True
            # and leave False arguments alone. False arguments
            # are filtered out, leaving a list of actions (str).
            actions = [
                option[0].lower() for option in
                CustomArgumentParser.AVAILABLE_STANDALONE_ARGUMENTS
                # If user has explicitly set this flag...
                if args_dictionary[option[0]]
                # Or implicitly set this flag through use of -all / -a
                or args_dictionary[option[0]] is None
            ]

            return actions
        else:
            # Warn the user in verbose mode if no additional options have been selected
            if not any(args_dictionary[arg[0]] for arg in
                       CustomArgumentParser.AVAILABLE_STANDALONE_ARGUMENTS):
                # Also warn user
                warn(
                    args_namespace.verbose,
                    "No arguments have been chosen, program will now terminate."
                )

            # Since -all / -a has not been opted into, only filter the flags the user has
            # specifically selected
            actions = [
                option[0].lower() for option in
                CustomArgumentParser.AVAILABLE_STANDALONE_ARGUMENTS
                if args_dictionary[option[0]]
            ]

            return actions

    def get_actions(self) -> List[str]:
        """Getter for the list of actions extracted from the command line
        arguments by this parser.

        Returns:
            `self.actions`:
                The list of text files/graphs this program should
                generate.
        """

        return self.actions
