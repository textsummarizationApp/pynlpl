###############################################################
#  PyNLPp - Statistics Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Also contains MIT licensed code from
#        AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
#        Peter Norvig
#
#       Licensed under GPLv3
# 
# This is a Python library containing classes for Statistic and
# Information Theoretical computations.
#
###############################################################

import math

class FrequencyList:
    def __init__(self, tokens = None, casesensitive = True):
        self._count = {}
        self._ranked = {}
        self.total = 0
        self.casesensitive = casesensitive
        if tokens: self.append(tokens)


    def _validate(self,type):
        if not self.casesensitive: 
            return tuple([x.lower() for x in type])
        else:
            return tuple(type)

    def append(self,tokens):
        for token in tokens:
            self.count(token)
        

    def count(self, type, amount = 1):
        type = self._validate(type)
        if self._ranked: self._ranked = None
        if type in self._count:
            self._count[type] += amount
        else:
            self._count[type] = amount
        self.total += amount

    def sum(self):
        """alias"""
        return self._total

    def _rank(self):
        if not self._ranked: self._ranked = sorted(self._count.items(),key=lambda x: x[1], reverse=True )

    def __iter__(self):
        """Returns a ranked list of (type, count) pairs. The first time you iterate over the FrequencyList, the ranking will be computed. For subsequent calls it will be available immediately, unless the frequency list changed in the meantime."""
        self._rank()
        for type, count in self._ranked:
            yield type, count

    def items(self):
        """Returns an *unranked* list of (type, count) pairs. Use this only if you are not interested in the order."""
        for type, count in  self._count.items():
            yield type, count

    def __getitem__(self, type):
        type = self._validate(type)
        return self._count[type]

    def __setitem__(self, type, value):
        """alias for count, but can only be called once"""
        type = self._validate(type)
        if not type in self._count:
            self.count(type,value)     
        else:
            raise ValueError("This type is already set!")
    
    def typetokenratio(self):
        """Computes the type/token ratio"""
        return len(self._total) / float(self._total)


    def mode(self):
        """Returns the type that occurs the most frequently in the frequency list"""
        self._rank()
        return self._ranked[0][0]


    def p(self, type): 
        """Returns the probability (relative frequency) of the token"""
        type = self._validate(type)
        return self._count[type] / float(self._total)


    def __eq__(self, otherfreqlist):
        return (self.total == otherfreqlist.total and self._count == otherfreqlist._count)

    def __contains__(self, type):
        type = self._validate(type)
        return type in self._count

    def __add__(self, otherfreqlist):
        product = FrequencyList(None, )
        for type, count in self.items():
            product.count(type,count)        
        for type, count in otherfreqlist.items():
            product.count(type,count)        
        return product

    def output(self,delimiter = '\t'):
        for type, count in self:    
            yield " ".join(type) + delimiter + str(count)

class Distribution:
    def __init__(self, data, base = None):
        self.base = base #logarithmic base: can be set to 2 or 10 (or anything else), when set to None, it defaults to e
        self._dist = {}
        if isinstance(data, FrequencyList):
            for type, count in data.items():
                self._dist[type] = count / float(data.total)
        elif isinstance(data, dict):
            self._dist = data 
            total = float(sum(self._dist.values()))
            if total < 0.999 or total > 1.000:
                #normalize again
                for key, value in self._dist.items():
                    self._dist[key] = value / total                       
        self._ranked = None
        

    def _validate(self,type):
        return tuple(type)

    def _rank(self):
        if not self._ranked: self._ranked = sorted(self._dist.items(),key=lambda x: x[1], reverse=True )

    def information(self, type):
        """Computes the information content of the specified type: -log_e(p(X))"""
        type = self._validate(type)
        if not base and self.base: base = self.base
        if not base:
            return -math.log(self._dist[type])
        else:
            return -math.log(self._dist[type], base)

    def poslog(self, type):
        """alias for information content"""
        type = self._validate(type)
        return self.information(type)

    def entropy(self, base = None):
        """Compute the entropy of the distribution (base e)"""
        entropy = 0
        if not base and self.base: base = self.base
        for type in self._dist:
            if not base:
                entropy += self._dist[type] * -math.log(self._dist[type])     
            else:
                entropy += self._dist[type] * -math.log(self._dist[type], base)     
        return entropy


    def mode(self):
        """Returns the type that occurs the most frequently in the probability distribution"""
        self._rank()
        return self._ranked[0][0]

    def maxentropy(self, base = None):     
        """Compute the maximum entropy of the distribution: log_e(N)"""   
        if not base and self.base: base = self.base
        if not base:
            return math.log(len(self._dist))
        else:
            return math.log(len(self._dist), base)



    def __getitem__(self, type):
        """Return the probability for this type"""
        type = self._validate(type)
        return self._dist[type]

    def __iter__(self):
        """Iterate over the ranked distribution, returns (type, probability) pairs"""       
        self._rank()
        for type, p in self._ranked:
            yield type, p

    def items(self):
        """Returns an *unranked* list of (type, prob) pairs. Use this only if you are not interested in the order."""
        for type, count in  self._dist.items():
            yield type, count

    def output(self,delimiter = '\t'):
        for type, prob in self:    
            yield " ".join(type) + delimiter + str(prob)



# All below functions are mathematical functions from  AI: A Modern Approach, see: http://aima.cs.berkeley.edu/python/utils.html 

def histogram(values, mode=0, bin_function=None): #from AI: A Modern Appproach 
    """Return a list of (value, count) pairs, summarizing the input values.
    Sorted by increasing value, or if mode=1, by decreasing count.
    If bin_function is given, map it over values first."""
    if bin_function: values = map(bin_function, values)
    bins = {}
    for val in values:
        bins[val] = bins.get(val, 0) + 1
    if mode:
        return sorted(bins.items(), key=lambda v: v[1], reverse=True)
    else:
        return sorted(bins.items())
 
def log2(x):  #from AI: A Modern Appproach 
    """Base 2 logarithm.
    >>> log2(1024)
    10.0
    """
    return math.log(x, 2)

def mode(values):  #from AI: A Modern Appproach 
    """Return the most common value in the list of values.
    >>> mode([1, 2, 3, 2])
    2
    """
    return histogram(values, mode=1)[0][0]

def median(values):  #from AI: A Modern Appproach 
    """Return the middle value, when the values are sorted.
    If there are an odd number of elements, try to average the middle two.
    If they can't be averaged (e.g. they are strings), choose one at random.
    >>> median([10, 100, 11])
    11
    >>> median([1, 2, 3, 4])
    2.5
    """
    n = len(values)
    values = sorted(values)
    if n % 2 == 1:
        return values[n/2]
    else:
        middle2 = values[(n/2)-1:(n/2)+1]
        try:
            return mean(middle2)
        except TypeError:
            return random.choice(middle2)

def mean(values):  #from AI: A Modern Appproach 
    """Return the arithmetic average of the values."""
    return sum(values) / float(len(values))

def stddev(values, meanval=None):  #from AI: A Modern Appproach 
    """The standard deviation of a set of values.
    Pass in the mean if you already know it."""
    if meanval == None: meanval = mean(values)
    return math.sqrt(sum([(x - meanval)**2 for x in values]) / (len(values)-1))

def dotproduct(X, Y):  #from AI: A Modern Appproach 
    """Return the sum of the element-wise product of vectors x and y.
    >>> dotproduct([1, 2, 3], [1000, 100, 10])
    1230
    """
    return sum([x * y for x, y in zip(X, Y)])

def product(seq):
    if len(seq) == 0:
        return 0
    else:
        product = 1
        for x in seq:
            product *= x
        return product

def vector_add(a, b):  #from AI: A Modern Appproach 
    """Component-wise addition of two vectors.
    >>> vector_add((0, 1), (8, 9))
    (8, 10)
    """
    return tuple(map(operator.add, a, b))



def normalize(numbers, total=1.0):  #from AI: A Modern Appproach 
    """Multiply each number by a constant such that the sum is 1.0 (or total).
    >>> normalize([1,2,1])
    [0.25, 0.5, 0.25]
    """
    k = total / sum(numbers)
    return [k * n for n in numbers]



