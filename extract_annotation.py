#!/usr/bin/env python3


#########
# about #
#########

__version__ = "0.1.2"
__author__ = ["Nikolaos Karaiskos","Marcel Schilling"]
__credits__ = ["Nikolaos Karaiskos","Mireya Plass Pórtulas","Marcel Schilling","Nikolaus Rajewsky"]
__status__ = "beta"
__licence__ = "GPL"
__email__ = "marcel.schilling@mdc-berlin.de"


###########
# imports #
###########

import gzip
import os


#############
# functions #
#############

# Test if a file is gzip compressed or not
def is_gzip_file(filename):
    try:
        # This will raise OSError for uncompressed files & has no side
        # effects for compressed files:
        gzip.GzipFile(filename).peek(1)
        return True
    except OSError:
        return False

# Open a file (gzip compressed or not)
def open_file(filename):
    if (is_gzip_file(filename)):
        return gzip.open(filename,'rt')
    else:
        return open(filename,'rt')

# Should write it to a file
def identify_polyA_intervals(genome, conditions):
    return 0


# Read annotation from GTF file
# For now, this will output BED to STDOUT, but this might be changed to
# either file output or returing the GTF data as a python object
def extract_three_prime_utr_information(gtf_file,
                                        feature_utr3 = "three_prime_utr"):

    # The following parameters define the parsing of the input GTF file.
    # They were chosen according to the standard described in
    # http://genome.ucsc.edu/FAQ/FAQformat.html#format4.

    # Lines starting with the following character will be skipped:
    comment_char = '#'

    # Lines will be split into fields by the following character:
    field_separator = '\t'

    # The attributes field will be split into type/value pairs by the
    # following string:
    attributes_separator = "; "

    # The attribute with the following index will be used as gene ID:
    attribute_index_gene_id = 0

    # Attribute type/value pairs will be split by the following
    # character:
    attribute_separator = ' '

    # The following index will be used to get the value of an attribute
    # type/value pair:
    attribute_value_index = 1

    # The following character will be removed from the beginning and end
    # of attribute values:
    attribute_value_quote = '"'

    # This variable will be used to keep track of the previous gene
    # The GTF input has to be sorted by gene ID (not checked).
    # This is necessary to be able to remove duplicate 3' UTRs arising
    # from different isoforms sharing the same 3'UTR without the need to
    # keep all 3' UTR BED entries in memory.
    # Instead, only those for one gene at a time are stored.
    previous_gene_id=None

    # This set will be used to store all 3' UTR BED entries for the
    # current gene (see above).
    three_prime_utrs=set()

    # Read GTF input line by line
    with open_file(gtf_file) as gtf:
        for line in gtf:

            # Skip comment lines
            if (line[0] == comment_char):
                continue

            # Split lines into fields
            (seqname, source, feature, start, end, score, strand, frame,
                    attributes) = line.rstrip().split(field_separator)

            # Skip lines not defining 3' UTRs
            if (feature != feature_utr3):
                continue

            # Convert from 1-based closed to 0-based open intervals
            start = (int(start) - 1)

            # Get gene ID from attributes list
            # I guess there is a more pythonic way to do that generating
            # a dictionary but this works.
            # Split accross several lines for clarity.
            attributes = attributes.split(attributes_separator)
            gene_id = attributes[attribute_index_gene_id]
            gene_id = gene_id.split(attribute_separator)
            gene_id = gene_id[attribute_value_index]
            gene_id = gene_id.strip(attribute_value_quote)

            # print BED line for each (different) 3' UTR isoform of the
            # previous gene
            if (gene_id!=previous_gene_id):
                if (previous_gene_id is not None):
                    for three_prime_utr in three_prime_utrs:
                        print('\t'.join(str(field) for field in
                                        three_prime_utr))

            # re-initialize 3' UTR set for current gene
                    three_prime_utrs=set()
                previous_gene_id=gene_id

            # append current 3' UTR to 3' UTRs of current gene (if not
            # seen before)
            three_prime_utrs.add((seqname,start,end,gene_id,strand,score))


    # print BED line for each (different) 3' UTR isoform of the last
    # gene
    if (previous_gene_id is not None):
        for three_prime_utr in three_prime_utrs:
            print('\t'.join(str(field) for field in three_prime_utr))


########
# main #
########

# Only run the following code if this module is run directly
if __name__ == '__main__':

    # GTF file to read annotation from
    gtf = "test_data/Homo_sapiens.GRCh38.83_chr9.gtf"

    # read GTF file and print BED output to STDOUT
    extract_three_prime_utr_information(gtf)
