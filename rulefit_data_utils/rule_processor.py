import table_processor as tp

class RuleProcessor(object):
    # Constructor:
    # @param rule_description_file is the path to R randomforest rule description file,
    # It reads file and parse it to in-memory rules at initiate
    def __init__(self, rule_description_file=None, feature_list_file=None):
        print "NOTE: be careful when using this utility, make sure \"MASK ID\" Label are removed from data during rule generating"
        assert isinstance(rule_description_file, str)
        self.rules = []
        self.groups = None
        self.feature_by_index = []

        if isinstance(feature_list_file, str):
            with open(feature_list_file, 'r') as f:
                for row in f:
                    self.feature_by_index.append(row.split(",")[1].strip("\n"))

        print "now reading rules from ", rule_description_file, "..."
        with open(rule_description_file, 'r') as f:
            for row in f:
                self.add_rule_by_text(row)
        print "reading complete"

    # Given @param data_table, compute rules output based on current rules
    def get_rule_output(self, data_table=None, output_filename=None):
        print "NOTE: make sure data_table is the same as the one applied in rule generating in R package"
        print "NOTE: be careful when using this utility, make sure \"MASK ID\" Label are removed from data during rule interpreting"
        assert isinstance(data_table, tp.Table)

        headers = ["r"+str(i) for i in xrange(1, len(self.rules)+1)]
        rule_outputs = [[] for x in xrange(0, len(data_table.data))]

        amount = len(self.rules)
        i = 0
        for r in self.rules:
            i += 1
            print "computing rules output...", str(i*100/amount), "%\r",
            for x in xrange(0, len(rule_outputs)):
                ro = '1' if r.is_matched(x, data_table) else '0'
                rule_outputs[x].append(ro)
        output_table = tp.Table(headers=headers, data=rule_outputs)
        print "computing rule output... 100%\ncomputing complete"

        if output_filename is not None:
            assert isinstance(output_filename, str)
            output_table.write_file(filename=output_filename)

        return output_table

    # Add rule with a line of rule description text
    # returns itself
    def add_rule_by_text(self, text):
        self.rules.append(Rule(text, self))
        return self

    # Remove rules from current rules based on user-defined condition
    # Remove nothing by default
    def remove_rules_by_condition(self, func=lambda r: False):
        cnt = 0
        for i in xrange(len(self.rules)-1, -1, -1):
            if func(self.rules[i]):
                cnt += 1
                self.rules.pop(i)
        print str(cnt), " rules are removed"
        return self

    # Group rules by user-defined hash function that returns one or many hashcode for one rule object
    # @param func is a function return either a hashcode or a list of hashcodes(to support overlapped groups) 
    # @returns a list of grouped rules
    # Group all rules together by default
    def group_rules_by_hashing(self, func=lambda r: 0):
        tmp = {}
        for rule in self.rules:
            hashings = func(rule)
            # if function returns a list, keep it as it is, else pack it in a list
            hashings = hashings if isinstance(hashings, list) else [hashings]
            for hashing in hashings:
                if hashing in tmp:
                    tmp[hashing].append(rule)
                else:
                    tmp[hashing] = [rule]
        self.groups = [tmp[key] for key in tmp]
        return self.groups

    # Output rule group config files
    def output_group_config(self, filename_index=None, filename_groupid=None):
        print "This function generates groups config files for MATLAB overlapped group lasso package(SLEP)"
        assert self.groups is not None, "run group_rules_by_hashing with user-defined function"
        assert isinstance(filename_index, str)
        assert isinstance(filename_groupid, str)
        with open(filename_groupid, "w") as fgid:
            with open(filename_index, "w") as findex:
                cursor = 1
                for group in self.groups:
                    findex.write(str(cursor)+",")
                    for rule in group:
                        fgid.write(str(self.rules.index(rule))+",")
                        cursor += 1
                    findex.write(str(cursor-1)+"\n")

class Rule(object):
    class SubRule(object):
        def __init__(self, opt):
            self.rule_type = opt['type']
            self.feature_id = opt['feature_id']
            if opt['type'] == 'enum':
                self.conditions = opt['conditions']
            elif opt['type'] == 'num':
                self.threshold = opt['threshold']
                self.direction = opt['direction']

    def __init__(self, text, rule_processor):
        self.subrules = []
        self.plain_text = text.strip('\n')   #  keep a copy of original rule text
        self.rp = rule_processor   # a poiter to rule processor, to track settings
        self.involved_features = []   # features involved with this rule can be used to group rules
        self.__parse()

    def __parse(self):
        for pt in self.plain_text.split('&'):
            opt = {}
            if '%in%' in pt:
                detail = pt.split(' %in% ')
                feature_id = detail[0].replace('X','').replace('[','').replace(']','').replace(',','')
                conditions = detail[1].replace('c','').replace('(','').replace(')','')
                opt['type'] = 'enum'
                opt['feature_id'] = int(feature_id)
                opt['conditions'] = []
                for c in conditions.split(','):
                    opt['conditions'].append(c.replace('\'',''))
            elif '<=' in pt:
                detail = pt.split('<=')
                feature_id = detail[0].replace('X','').replace('[','').replace(']','').replace(',','')
                threshold = float(detail[1])
                opt['type'] = 'num'
                opt['feature_id'] = int(feature_id)
                opt['threshold'] = threshold
                opt['direction'] = "<="
            elif '>' in pt:
                detail = pt.split('>')
                feature_id = detail[0].replace('X','').replace('[','').replace(']','').replace(',','')
                threshold = float(detail[1])
                opt['type'] = 'num'
                opt['feature_id'] = int(feature_id)
                opt['threshold'] = threshold
                opt['direction'] = ">"
            else:
                pass
            if len(self.rp.feature_by_index) > 0: # when feature names are read when constructing rule_processor
                self.involved_features.append(self.rp.feature_by_index[opt['feature_id']]) # know feature id, find feature name
            self.subrules.append(self.SubRule(opt))

    def is_matched(self, row, data_table):
        for sr in self.subrules:
            attr = data_table.headers[sr.feature_id]
            value = data_table.get_element(attr, row)
            if sr.rule_type == 'enum':
                if value not in sr.conditions:
                    return False
            elif sr.rule_type == 'num':
                if value == '':
                    return False
                if sr.direction == ">":
                    if float(value) <= sr.threshold:
                        return False
                elif sr.direction == "<=":
                    if float(value) > sr.threshold:
                        return False
                else:
                    return False
            else:
                return False
        return True        
