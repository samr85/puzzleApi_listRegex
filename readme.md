# Regex Word List

This applies regex's to the word lists in the wordList directory.

The wordlist files are expected to be tab separated value files.  Lines at the start of the file beginning # are taken as comments and ignored.  The first line not starting with a #  is taken as the heading for the columns returned by the json blob.  After the heading has been read, no more comments are allowed.

Matches are applied to the first column, and matches are returned in the order they are listed in the source file.
