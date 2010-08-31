###############################################################
#  PyNLPl - Moses formats
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
# This is a Python library classes and functions for 
# reading file-formats produced by Moses. Currently 
# contains only a class for reading a Moses PhraseTable.
# (migrated to pynlpl from pbmbmt)
#
###############################################################    

import sys
import bz2
import datetime

class PhraseTable:
    def __init__(self,filename, quiet=False, reverse=False, delimiter="|||", score_column = 5, align2_column = 4):
        """Load a phrase table from file into memory (memory intensive!)"""
        self.phrasetable = {}
        if filename.split(".")[-1] == "bz2":
            f = bz2.BZ2File(filename,'r')        
        else:
            f = open(filename,'r')
        linenum = 0
        while True:
            if not quiet:
                linenum += 1
                if (linenum % 100000) == 0:
                    print >> sys.stderr, "Loading phrase-table: @%d" % linenum, "\t(" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ")"
            line = f.readline()
            if not line: 
                break

             #split into (trimmed) segments
            segments = [ segment.strip() for segment in line.split(delimiter) ]

            #Do we have a score associated?
            if score_column > 0 and len(segments) >= score_column:
                nums = segments[score_column-1].strip().split(" ")
                Pst = float(nums[0]) #the 1st number is p(source|target)
                Pts = float(nums[2]) #3rd number is p(target|source)
            else:
                Pst = Pts = 0

            if align2_column > 0:
                try:
                    null_alignments = segments[align2_column].count("()")
                except:
                    null_alignments = 0
            else:
                null_alignments = 0

            if reverse:
                source = tuple(segments[1].split(" "))
                target = tuple(segments[0].split(" "))
            else:
                source = tuple(segments[0].split(" "))
                target = tuple(segments[1].split(" "))

            self.append(source, target,Pst,Pts,null_alignments)
                        
        f.close()        


    def append(self, source, target, Pst = 0, Pts = 0, null_alignments = 0):
        d = self.phrasetable
        for word in source:
            if not word in d:
                d[word] = {}
            d = d[word]

        if "" in d:
            d[""].append( (target, Pst, Pts, null_alignments) )
        else:
            d[""] = [ (target, Pst, Pts, null_alignments) ]

    def __contains__(self, phrase):
        """Query if a certain phrase exist in the phrase table"""
        d = self.phrasetable
        for word in phrase:
            if not word in d:
                return False
            d = d[word]
        return ("" in d)

    def __getitem__(self, phrase): #same as translations
        """Return a list of (translation, Pst, Pts, null_alignment) tuples"""
        d = self.phrasetable
        for word in phrase:
            if not word in d:
                raise KeyError
            d = d[word]

        if "" in d:
            return d[""]
        else:
            raise KeyError

