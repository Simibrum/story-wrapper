# Based on https://github.com/JonathanReeve/chapterize/blob/master/chapterize/chapterize.py
import logging
import re
import os
from src.story_wrapper.data_loaders.gutenberg import get_book


def zero_pad(numbers):
    """
    Takes a list of ints and zero-pads them, returning
    them as a list of strings.
    """
    maxNum = max(numbers)
    maxDigits = len(str(maxNum))
    numberStrs = [str(number).zfill(maxDigits) for number in numbers]
    return numberStrs


class Book:
    def __init__(self, book_id, nochapters, stats):
        self.book_id = book_id
        self.nochapters = nochapters
        self.end_location = None
        self.end_line = None
        self.contents = self.get_contents()
        self.lines = self.get_lines()
        self.headings = self.get_headings()
        # Alias for historical reasons. FIXME
        self.heading_locations = self.headings
        self.ignore_toc()
        logging.info('Heading locations: %s' % self.heading_locations)
        headings_plain = [self.lines[loc] for loc in self.heading_locations]
        logging.info('Headings: %s' % headings_plain)
        self.chapters = self.get_text_between_headings()
        # logging.info('Chapters: %s' % self.chapters)
        self.num_chapters = len(self.chapters)
        self.paragraphs = self.get_paragraphs()

        if stats:
            self.get_stats()

    def get_contents(self):
        """
        Reads the book into memory.
        """
        return get_book(self.book_id)

    def get_lines(self):
        """
        Breaks the book into lines.
        """
        return self.contents.split('\n')

    def get_headings(self):

        # Form 1: Chapter I, Chapter 1, Chapter the First, CHAPTER 1
        # Ways of enumerating chapters, e.g.
        arabicNumerals = r'\d+'
        romanNumerals = r'(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
        numberWordsByTens = ['twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        numberWords = ['one', 'two', 'three', 'four', 'five', 'six',
                       'seven', 'eight', 'nine', 'ten', 'eleven',
                       'twelve', 'thirteen', 'fourteen', 'fifteen',
                       'sixteen', 'seventeen', 'eighteen', 'nineteen'] + numberWordsByTens
        numberWordsPat = '(' + '|'.join(numberWords) + ')'
        ordinalNumberWordsByTens = ['twentieth', 'thirtieth', 'fortieth', 'fiftieth',
                                    'sixtieth', 'seventieth', 'eightieth', 'ninetieth'] + numberWordsByTens
        ordinalNumberWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth',
                              'seventh', 'eighth', 'ninth', 'twelfth', 'last'] + \
                             [numberWord + 'th' for numberWord in numberWords] + ordinalNumberWordsByTens
        ordinalsPat = r'(the )?(' + '|'.join(ordinalNumberWords) + ')'
        enumeratorsList = [arabicNumerals, romanNumerals, numberWordsPat, ordinalsPat]
        enumerators = '(' + '|'.join(enumeratorsList) + ')'
        form1 = 'chapter ' + enumerators

        # Form 2: II. The Mail
        enumerators = romanNumerals
        separators = r'(\. | )'
        titleCase = r'[A-Z][a-z]'
        form2 = enumerators + separators + titleCase

        # Form 3: II. THE OPEN ROAD
        enumerators = romanNumerals
        separators = r'(\. )'
        titleCase = r'[A-Z][A-Z]'
        form3 = enumerators + separators + titleCase

        # Form 4: a number on its own, e.g. 8, VIII
        arabicNumerals = r'^\d+\.?$'
        romanNumerals = r'(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.?$'
        enumeratorsList = [arabicNumerals, romanNumerals]
        enumerators = '(' + '|'.join(enumeratorsList) + ')'
        form4 = enumerators

        pat = re.compile(form1, re.IGNORECASE)
        # This one is case-sensitive.
        pat2 = re.compile(r'(%s|%s|%s)' % (form2, form3, form4))

        # TODO: can't use .index() since not all lines are unique.

        headings = []
        for i, line in enumerate(self.lines):
            if pat.match(line) is not None:
                headings.append(i)
            if pat2.match(line) is not None:
                headings.append(i)

        if len(headings) < 3:
            logging.info('Headings: %s' % headings)
            logging.error(
                "Detected fewer than three chapters. This probably means there's "
                "something wrong with chapter detection for this book."
            )
            exit()

        self.end_location = self.get_end_location()

        # Treat the end location as a heading.
        headings.append(self.end_location)

        return headings

    def ignore_toc(self):
        """
        Filters headings out that are too close together,
        since they probably belong to a table of contents.
        """
        pairs = zip(self.heading_locations, self.heading_locations[1:])
        toBeDeleted = []
        for pair in pairs:
            delta = pair[1] - pair[0]
            if delta < 4:
                if pair[0] not in toBeDeleted:
                    toBeDeleted.append(pair[0])
                if pair[1] not in toBeDeleted:
                    toBeDeleted.append(pair[1])
        logging.debug('TOC locations to be deleted: %s' % toBeDeleted)
        for badLoc in toBeDeleted:
            index = self.heading_locations.index(badLoc)
            del self.heading_locations[index]

    def get_end_location(self):
        """
        Tries to find where the book ends.
        """
        ends = ["End of the Project Gutenberg EBook",
                "End of Project Gutenberg's",
                r"\*\*\*END OF THE PROJECT GUTENBERG EBOOK",
                r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK"]
        joined = '|'.join(ends)
        pat = re.compile(joined, re.IGNORECASE)
        endLocation = None
        for line in self.lines:
            if pat.match(line) is not None:
                endLocation = self.lines.index(line)
                self.end_line = self.lines[endLocation]
                break

        if endLocation is None:  # Can't find the ending.
            logging.info("Can't find an ending line. Assuming that the book ends at the end of the text.")
            endLocation = len(self.lines)-1  # The end
            self.end_line = None

        logging.info('End line: %s at line %s' % (self.end_line, endLocation))
        return endLocation

    def get_text_between_headings(self):
        chapters = []
        lastHeading = len(self.heading_locations) - 1
        for i, headingLocation in enumerate(self.heading_locations):
            if i != lastHeading:
                nextHeadingLocation = self.heading_locations[i + 1]
                chapters.append(self.lines[headingLocation+1:nextHeadingLocation])
        return chapters

    def get_paragraphs(self):
        """
        Returns a list of paragraphs.
        """
        paragraphs = []
        for chapter in self.chapters:
            line_group = []
            for line in chapter:
                if line.strip() != '':
                    line_group.append(line)
                elif line_group:
                    paragraphs.append(" ".join(line_group).strip())
                    line_group = []
            # Add the last line group.
            if line_group and line != '':
                paragraphs.append(" ".join(line_group).strip())
        return paragraphs

    def get_stats(self):
        """
        Returns statistics about the chapters, like their length.
        """
        # TODO: Check to see if there's a log file. If not, make one.
        # Write headings to file.
        numChapters = self.num_chapters
        averageChapterLength = sum([len(chapter) for chapter in self.chapters])/numChapters
        headings = ['ID', 'Average chapter length', 'Number of chapters']
        stats = ['"' + self.book_id + '"', averageChapterLength, numChapters]
        stats = [str(val) for val in stats]
        headings = ','.join(headings) + '\n'
        statsLog = ','.join(stats) + '\n'
        logging.info('Log headings: %s' % headings)
        logging.info('Log stats: %s' % statsLog)

        if not os.path.exists('log.txt'):
            logging.info('Log file does not exist. Creating it.')
            with open('log.txt', 'w') as f:
                f.write(headings)
                f.close()

        with open('log.txt', 'a') as f:
            f.write(statsLog)
            f.close()
