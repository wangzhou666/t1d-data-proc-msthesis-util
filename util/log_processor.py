import table_processor as tp

class LogProcessor(object):
    # Constructor for LogProcessor,
    # @param source, source file to read data from
    # @param timestamp, the name of attribute indicating log timestamp
    # @param start, end, the starting and ending checkpoints of interesting timeframe
    # @param interval, the interval of checkpoints of interesting timeframe
    def __init__(self, source_file=None, group_key="Mask Id", black_list=None, white_list=None):
        assert isinstance(source_file, str)
        logs = tp.Table(filename=source_file, black_list=black_list, white_list=white_list)
        self.key = group_key
        self.headers = logs.headers[:]
        self.grouped_logs = logs.group_by_attr(key=group_key)

    # flat temporal table,
    # convert coninuous temporal data with log-like records(with timestamp) to single-line vectors
    # SUGGEST to apply to tables with "ab_zscores", "outcomes_longitudinal_mask", "tb_life_events"
    # @returns Table object with flatted table, may need to apply write_file() to csv output
    def flat_by_timestamp(self, timestamp='Due_num', start=None, end=None, interval=None):
        assert isinstance(timestamp, str)
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start >= 0
        assert end >= start
        assert isinstance(interval, int)
        assert interval > 0
        assert timestamp in self.headers

        checkpoints = [int(cp) for cp in range(start, end, interval)]
        orig_attrs = self.headers[:]
        orig_attrs.remove(self.key)
        orig_attrs.remove(timestamp)

        flat_attrs = [attr+'_'+str(cp) for attr in orig_attrs for cp in checkpoints]
        res = tp.Table(headers=[self.key]+flat_attrs, data=[])

        print "flatting temporal tables, this might take some time..."
        print 'SUGGEST to apply to tables with "ab_zscores", "outcomes_longitudinal_mask", "tb_life_events"(may need to change @param timestamp)'
        amount = len(self.grouped_logs)
        i = 0
        for logs in self.grouped_logs:
            i += 1
            print "flatting...", str(i*100/amount), "%\r",
            logs.sort_by_attr(primary_key=timestamp)
            entry = [logs.get_element(self.key, 0)]
            for attr in orig_attrs:
                start = 0
                for cp in checkpoints:
                    while float(logs.get_element(timestamp, start)) < cp and start < logs.get_rows_num():
                        start += 1
                    entry.append(logs.get_element(attr, start))
            res = res.horizontal_join(tp.Table(headers=res.headers[:], data=[entry]))

        print "flatting...100%"
        print "flatting complete"
        return res

    # helper function:
    # find closet number to target in an array
    def __find_closest(self, array, target):
        if target <= array[0]:
            return array[0]
        index = 1
        while index < len(array):
            if target >= array[index-1] and target <= array[index]:
                return array[index-1] if target - array[index-1] < array[index] - target else array[index]
            else:
                index += 1
        return array[index-1]

    # generate odds report,
    # convert discret temporal data with log-like records(with timestamp) to single line vectors
    # SUGGEST to apply to table with "infectious_episodes_masked"
    # @returns Table object with report table, may need to apply write_file() to csv output
    def report_odds_by_timestamp(self, timestamp='Inf Age Mos', category='Inf Epi Group', start=None, end=None, interval=None):
        assert isinstance(timestamp, str)
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start >= 0
        assert end >= start
        assert isinstance(interval, int)
        assert interval > 0
        assert timestamp in self.headers
        assert category in self.headers

        checkpoints = [int(cp) for cp in range(start, end, interval)]
        odds_categ = set()
        for logs in self.grouped_logs:
            for row in xrange(0, logs.get_rows_num()):
                odds_categ.add(logs.get_element(category, row))

        cat_time_attrs = [category+'_'+cat+'_'+str(cp) for cat in odds_categ for cp in checkpoints]
        res = tp.Table(headers=[self.key]+cat_time_attrs, data=[])

        print "reporting odds temporal tables, this might take some time..."
        print 'SUGGEST to apply to tables with "infectious_episodes_masked"(may need to change @param timestamp)'
        amount = len(self.grouped_logs)
        i = 0
        for logs in self.grouped_logs:
            i += 1
            print "generating report...", str(i*100/amount), "%\r",
            entry = [logs.get_element(self.key, 0)] + ['0'] * len(cat_time_attrs)
            for row in xrange(0, logs.get_rows_num()):
                time = float(logs.get_element(timestamp, row))
                checkpoint = self.__find_closest(checkpoints, time)
                categ = logs.get_element(category, row)
                entry[1+cat_time_attrs.index(category+'_'+categ+'_'+str(checkpoint))] = '1'
            res = res.horizontal_join(tp.Table(headers=res.headers[:], data=[entry]))

        print "generating report...100%"
        print "reporting odds complete"
        return res

