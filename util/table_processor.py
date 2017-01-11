import numpy

class Table(object):
    # Constructor:
    # Option 1. construct table with csv file by specifying csv @param filename,
    # Option 2. construct table with in-memory @param data (as python list of list) and @param headers (as python list) 
    # by specifying data and headers,
    # To drop attributes, list those attribute names in text file, and specify config file name @param black_list
    # To accept attributes only, list attribute names in text file, @param white_list
    def __init__(self, filename=None, data=None, headers=None, black_list=None, white_list=None):
        if filename is None:
            assert data is not None
            assert headers is not None
            self.data = data
            self.headers = headers
        else:
            self.data = []
            self.headers = []
            self.__read_file(filename)
        if black_list is not None:
            self.__remove_attrs(black_list)
        if white_list is not None:
            self.__allow_attrs(white_list)
        assert len(self.headers) == len(set(self.headers)), "error: this table contains duplicated attribute names"

    # Private method:
    # read csv file to Table object
    def __read_file(self, filename):
        print "reading ", filename, "... \nNote: it supports csv files with delimiter ','"
        assert '.csv' in filename, "unsupported file type"
        with open(filename, 'r') as f:
            i = 0
            for row in f:
                elements = row.split(',')
                elements[-1] = elements[-1].strip('\n')
                elements[-1] = elements[-1].strip('\r')
                if i == 0:
                    for element in elements:
                        self.headers.append(element)
                else:
                    self.data.append([])
                    for element in elements:
                        self.data[-1].append(element)
                i += 1
        print "reading complete"

    # Private method:
    # remove attributes based on white list config file from Table
    def __allow_attrs(self, wl_filename):
        assert isinstance(wl_filename, str)
        attrs = set()
        with open(wl_filename, 'r') as f:
            for row in f:
                attr = row
                attr = attr.strip('\n')
                attr = attr.strip('\r')
                attrs.add(attr)
        for x in xrange(len(self.headers)-1, -1, -1):
            if self.headers[x] not in attrs:
                self.remove_attr(self.headers[x])

    # Private method:
    # remove attributes based on black list config file from Table
    def __remove_attrs(self, bl_filename):
        assert isinstance(bl_filename, str)
        attrs = set()
        with open(bl_filename, 'r') as f:
            for row in f:
                attr = row
                attr = attr.strip('\n')
                attr = attr.strip('\r')
                attrs.add(attr)
        for attr in attrs:
            self.remove_attr(attr)

    # remove an attribute from table
    def remove_attr(self, attr_name):
        if attr_name in self.headers:
            index = self.headers.index(attr_name)
            self.headers.pop(index)
            for d in self.data:
                d.pop(index)
        print "attr:", attr_name, "is removed"

    # write Table object to csv file
    def write_file(self, filename):
        assert isinstance(filename, str)
        print "writing csv file:", filename, "..."
        with open(filename, 'w') as f:
            amount = len(self.headers)
            i = 0
            for h in self.headers:
                i += 1
                f.write(h)
                if i != amount:
                    f.write(',')
                else:
                    f.write('\n')
            for entry in self.data:
                i = 0
                for element in entry:
                    i += 1
                    f.write(element)
                    if i != amount:
                        f.write(',')
                    else:
                        f.write('\n')
        print "writing complete"

    # helper function: check if a string is number
    # assuming a number can convert to float
    def __isNumber(self, text):
        try:
            v = float(text)
            if numpy.isnan(v) or numpy.isinf(v):
                return False
            else:
                return True
        except ValueError:
            return False


    # sort table entries by attribute
    def sort_by_attr(self, primary_key="Mask Id", secondary_key=None):
        assert isinstance(primary_key, str)
        assert primary_key in self.headers
        primary_index = self.headers.index(primary_key)
        if secondary_key is None:
            self.data = sorted(self.data, key=lambda d: float(d[primary_index]) if self.__isNumber(d[primary_index]) else d[primary_index])
        else:
            secondary_index = self.headers.index(secondary_key)
            self.data = sorted(self.data, key=lambda d: (float(d[primary_index]) if self.__isNumber(d[primary_index]) else d[primary_index], \
                float(d[secondary_index]) if self.__isNumber(d[secondary_index]) else d[secondary_index]))

    # join two Table objects, by default, using "Mask Id" as join key,
    # it only join each key once, so please make sure key is unique,
    # so for temproal dataset, please flat it by time points prior to this.
    def join_by_attr(self, other, key="Mask Id"):
        assert isinstance(key, str)
        assert key in self.headers and key in other.headers
        print "joining tables, this might take some time..."
        index_self = self.headers.index(key)
        index_other = other.headers.index(key)
        headers = self.headers + other.headers
        headers.pop(len(self.headers)+index_other)
        data = []
        joined = set()
        cache = {} # cache key-index
        amount_self = len(self.data)
        amount_other = len(other.data)
        i = 0 # track index to build cache
        j = 0 # track progress
        for entry_s in self.data:
            print "joining...", str(j*100/amount_self), "%\r",
            if entry_s[index_self] in joined:
                continue
            if entry_s[index_self] in cache:
                data.append(entry_s + other.data[cache[entry_s[index_self]]])
                data[-1].pop(len(self.headers)+index_other)
                joined.add(entry_s[index_self])
            while i < amount_other:
                entry_o = other.data[i]
                if entry_o[index_other] in joined:
                    pass
                elif entry_s[index_self] == entry_o[index_other]:
                    data.append(entry_s + entry_o)
                    data[-1].pop(len(self.headers)+index_other)
                    joined.add(entry_s[index_self])
                    i += 1
                    continue
                else:
                    cache[entry_o[index_other]] = i
                i += 1
            j += 1
        print "joining...100%"
        print "joining complete"
        return Table(data=data, headers=headers)

    # remove rows by user-defined condition which is determined by
    # an anonymous function @param func which returns True or False,
    # by default, it doesn't remove any row
    def remove_rows_by_condition(self, func=lambda x: False):
        cnt = 0
        for i in xrange(len(self.data)-1, -1, -1):
            if func(self.data[i]):
                cnt += 1
                self.data.pop(i)
        print str(cnt), " rows are removed"

    def horizontal_join(self, other):
        assert len(self.headers) == len(other.headers)
        for x in xrange(0, len(self.headers)):
            assert self.headers[x] == other.headers[x]
        return Table(headers=self.headers[:], data=self.data+other.data)

    # @returns a list of Table objects, grouped by given @param key
    def group_by_attr(self, key='Mask Id'):
        assert isinstance(key, str) and key in self.headers
        amount = len(self.data)
        res = []
        if amount == 0:
            return res
        self.sort_by_attr(primary_key=key)
        index = self.headers.index(key)
        cur_val = self.data[0][index]
        start = 0
        for end in xrange(1,amount+1):
            if end == amount or self.data[end][index] != cur_val:
                res.append(Table(headers=self.headers[:], data=self.data[start:end]))
                if end != amount:
                    cur_val = self.data[end][index]
                    start = end
        return res

    # @returns number of samples
    def get_rows_num(self):
        return len(self.data)

    # @returns number of attributes
    def get_cols_num(self):
        return len(self.headers)

    # @returns elements in @param row, and @param attr
    def get_element(self, attr=None, row=None):
        assert isinstance(row, int)
        assert attr in self.headers
        index = self.headers.index(attr)
        return self.data[row][index]
