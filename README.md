About
-----

Simple spaced repetition flashcard software. Flashcards are stored in a simple
text format and the code is small enough to be easily modifiable. The spaced
repetition algorithm is SM-2 (http://www.supermemo.com/english/ol/sm2.htm). See
the python files for usage of the package. See the SM-2 website for more
details on the algorithm and the scale of the user self-evaluation input.

Flashcards have two parts, corresponding to the top and bottom of a card. Cards
are stored in a TSV file with the top and bottom and the state for the spaced
repetition algorithm.

Command line and terminal interface
-----------------------------------

The package includes a terminal command line and terminal interface which is
currently Unix-only (although portability should just need support for clearing
the terminal and reading single characters). Use the `cmd-line` extra to enable
this interface. See `--help` or man pages for details.

An example of common usage is as follows:

  fulgurate-import example.tsv example.cards # Create a flashcard set
  fulgurate-run example.cards # Run the flashcards in the terminal
  fulgurate-show-schedule example.cards # Show the current scheduling for the cards

The input to import (`example.tsv` in the example) should be a TSV or CSV
(configurable) which contains columns for the top and bottom fields. The card
state file (`example.cards` in the example) is similar but includes the card
state for the spaced repetition algorithm.

The included example.tsv file is sample card data consisting of a few
Chinese-English dictionary entries from CC-CEDICT. The files example-filter.sh
and example-finish.sh are for fulgurate-run's -f and -F options respectively,
and are designed to work with the same data.
