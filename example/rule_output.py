from rulefit_data_utils import table_processor as tp
from rulefit_data_utils import rule_processor as rp

########## rule processor ##############

rule_p = rp.RuleProcessor(rule_description_file="example/output/example-rules.txt")
table_feature = tp.Table(filename="example/output/example-features.csv")

table_output = rule_p.get_rule_output(data_table=table_feature, output_filename="example/output/example-rule-output(for_lasso).csv")
