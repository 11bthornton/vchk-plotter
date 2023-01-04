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
"""Classes to facilitate the parsing of .vchk files.

AUTHOR: Ben-Lukas Thornton.
DATE: Oct16-22.
LAST REVISED: OCT16-22.
Ben.Thornton955@cranfield.ac.uk, ben.thornton@astrazeneca.com

Collection of classes to parse a given .vchk file into the appropriate
sections which in turn are interpreted as Pandas' Dataframes.

Typical usage example:

    fh = FileHandler(command_line_args, actions)
    stats_file_object = fh.parse()
"""

import ast
import re
import sys

from typing import List

import pandas as pd

from .plotting_structured import DataPlotter
from .utils import error, write_as_text


class StatsFileObject:
    """Represents a parsed .vchk file.

      Provides helper methods to retreive particular
      sections through their section title.
      """

    def __init__(self, **kwargs) -> None:
        """Initialises two empty dictionaries.

            From section_title => text / DataFrame
            """

        self._sections = dict(**kwargs)

    def add_section(self, name, section) -> None:
        """Register a section (DataFrame) in this instance's 
            dictionary.

            Args:
                name:
                    The name of the section.
                section:
                    Pandas DataFrame of the data parsed in this
                    section of the .vchk file.
            """

        self._sections[name] = section

    def get_section(self, name):

        return self._sections[name]


class FileHandler:
    """Parses a .vchk file into its appropriate sections.

      Reads a .vchk file and parses a statistics section whenever it sees a section header.
      The class `Section` is responsible for iterating over the relevant lines in the file
      and interpreting these lines as a Pandas' Dataframe.
      Each `Section` instance is then stored within a `StatsFileObject` instance to allow
      for the easy retrieval of sections required for plotting.

      Attributes:
          _in_file: The (str) location of the input .vchk file. Relative or Absolute.
              Internal class use only.
          _out_file: The (str) location of the program's output directory. Relative or Absolute.
              Internal class use only.
          _actions: The list of user-provided flags. Only parse these sections.
              Internal class use only.
      """

    # Regular expression pattern for a section header.
    SECTION_HEADER_PATTERN = re.compile(r"# (\w+)\t")

    # Regular expression pattern to enable iteration over
    # the column names of a section. Allows for the removal
    # of the digit (e.g. [23]...) section in square brackets.
    SECTION_HEADER_CONSTITUENT = re.compile(r"\[\d+\](.+)")

    def __init__(self, clargs, actions) -> None:
        """Initialises a FileHandler instance with a given
            out-file, in-file and list of sections to parse.

            Args:
                clargs:
                    The `argparse.Namespace` instance of command-line arguments.
                actions:
                    A list of sections to parse.
            """

        self._in_file = clargs.in_dir
        self._out_file = clargs.out_dir
        self._actions = actions

    def parse(self) -> StatsFileObject:
        """Parses a .vchk file.

            Tries opening the file and exits with an error message if file
            cannot be found. Parses the .vchk file into a `StatsFileObject`.

            Returns:
                A `StatsFileObject` containing a dict of sections that have
                been parsed. 
            """

        try:
            with open(self._in_file, "r", encoding="utf-8") as stats_file:

                stats_file_object = StatsFileObject()

                for line in stats_file:

                    # Is this line a header to a stats section?
                    match = FileHandler.SECTION_HEADER_PATTERN.match(line)
                    if match:
                        # If so, retrieve the section "title"
                        # and the names of the columns.
                        line_split = line.split("\t")
                        data_type_title = line_split[0][2:].lower()
                        columns = list(
                            map(self.check_and_clean, line_split[1:]))

                        # Only go to the trouble of parsing the section if
                        # the user has requested to view the stats of this
                        # section.
                        if data_type_title in self._actions or data_type_title == "sn":
                            section = Section(data_type_title, columns, line)

                            # The following will implicitly call `next` on the `stats_file`
                            # iterator. So when section is done parsing,
                            # this loop will resume and start looking for
                            # headers again.
                            try:
                                section = section.parse(stats_file)
                                stats_file_object.add_section(
                                    data_type_title, section)
                            except IOError:
                                self._actions.remove(data_type_title)
                                error(
                                    f"Could not parse section {data_type_title} properly")

                return stats_file_object

        except FileNotFoundError:
            error("No such file")
            sys.exit(1)

    def check_and_clean(self, line_to_clean) -> str:
        """Beautifies the column name by removing index in square brackets.

            Also serves the purpose of finding discrepencies in column name formats.
            If there is no appropriate name for a column, then the file cannot be
            parsed and so the program should exit. 

            E.g. Transforms a column name of "[23]Name" => "Name".

            Also strips trailing white space and removes the new line character.

            Args:
                line_to_clean:
                    The line to clean.

            Returns:
                The cleaned line.
            """

        line_to_clean = line_to_clean.strip().replace("\n", "")
        groups = FileHandler.SECTION_HEADER_CONSTITUENT.match(line_to_clean)

        if groups is None:
            error("File not in correct format")
            exit(1)

        try:
            cleaned_title = groups.group(1).lower()
        except IndexError:
            error("File not in correct format")
            exit(1)

        return cleaned_title


def coerce_to_appropriate_dtype(val):
    """Coerces a string to a literal value.

      A hacky workaround for when Pandas decides to treat
      all values as type Object when a Dataframe is instantiated
      from a list of lists of strings.

      Way to do this through Pandas?
      #TODO: ?

      E.g.
          `"3" : str -> 3 : int`
      """

    # https://docs.python.org/3/library/ast.html#ast.literal_eval
    try:
        val = ast.literal_eval(val)
    except Exception:
        return str(val)

    return val


class Section:
    """Represents an individual section from a .vchk file.

      Attributes:
          _title: The name of this section. Internal class use only.
          _columns: A list of column names
          _rows: A list of all rows

      """

    def __init__(self, title, columns, header) -> None:
        """Initialises a `Section` instance with a title, column names and empty list of rows."""

        self._title = title
        self._columns = columns
        self._plotter = None
        self._rows = []
        self._text_rows = [header]

        self._data_frame = None

    def accept_row(self, row) -> None:
        """Parses a new row.

            Useful for checking the format of the file too. Will throw
            an error if the number of items in the row is not equal
            to the expected number (`len(self._columns)`). If this is
            the case, then the program exits as file cannot be parsed.

            Args:
                row:
                    The row to parse.

            Raises:
                IOError:
                    If the file is not in the correct format. Handled
                    by the caller.
            """

        # Ignore the identifier at the beginning of the line.
        # This is just the title...
        split_on_delimiter = row.split("\t")[1:]

        if (len(split_on_delimiter) != len(self._columns)):

            raise IOError(
                "File not in the correct format. Missing a data point")

        # Cheap hack. See docs for `coerce_to_appropriate_dtype`.
        self._rows.append([
            coerce_to_appropriate_dtype(split) for split in split_on_delimiter
        ])

    def parse(self, file_line_iterator):
        """Takes an iterator over the lines of the .vchk file
            and accepts rows until the section is terminated.

            Args:
                file_line_iterator:
                    An iterator over the lines of the input .vhck file.
                    This advances the iterator used in the parsing of the
                    file as a whole. When this returns, the parser is able
                    to continue parsing the next section.

            Returns:
                A tuple of the raw text of this section and the data parsed
                as a pandas DataFrame.
            """

        # Advance the iterator by reading the next line.
        next_line = next(file_line_iterator, None)

        # The non-header lines of a section do not begin with a '#'
        # so can use this as a termination condition.
        while next_line is not None and not next_line.startswith("#"):

            # Append the raw text and then separately clean the line
            # so it can be interpreted by pandas.
            self._text_rows.append(next_line)
            self.accept_row(next_line.strip().replace("\n", ""))

            # Advance the iterator to parse the next line
            next_line = next(file_line_iterator, None)

        self._data_frame = pd.DataFrame(columns=self._columns,
                                        data=self._rows,
                                        dtype=None)

        return self

    def plot_and_write_file(self, out_dir):
        """Plots this section using the appropriate plotter

        Args:
            out_dir:
                The base out directory.
        """

        self._plotter = DataPlotter.get_plotter(self._title, self._data_frame,
                                                out_dir)

        if self._plotter is not None:
            self._plotter.plot().save()

        write_as_text(out_dir, self._title, self._text_rows)

    def get_text(self) -> List[str]:
        """Accesser method for the private raw text of this section"""
        return self._text_rows
