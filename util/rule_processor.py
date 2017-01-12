import table_processor as tp

class RuleProcessor(object):
    def __init__(self, rule_description_file=None):
        print "NOTE: be careful when using this utility, make sure \"MASK ID\" Label are removed from data during rule generating"
        assert isinstance(rule_description_file, str)
        self.rules = []
        print "now reading rules from ", rule_description_file, "..."
        with open(rule_description_file, 'r') as f:
            for row in f:
                self.rules.append(Rule(row))
        print "reading complete"

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

    def __init__(self, text):
        self.subrules = []
        self.plain_text = text.strip('\n')
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
