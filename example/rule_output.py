import sys

sys.path.append("/Users/zhouwang/Desktop/thesis-code")

from rulefit_data_utils import table_processor as tp
from rulefit_data_utils import rule_processor as rp

########## rule processor ##############

rule_p = rp.RuleProcessor(rule_description_file="example/output/example-rules.txt", \
    feature_list_file="example/output/example-feature-list.txt")
table_feature = tp.Table(filename="example/output/example-features.csv")

# remove rules containing feature "PTPN221"
rule_p.remove_rules_by_condition(func=lambda r: "PTPN221" in r.involved_features)

table_output = rule_p.get_rule_output(data_table=table_feature, \
    output_filename="example/output/example-rule-output(for_lasso).csv")


######## with group #############

# Example 1: group rules by length of text description
rule_p.group_rules_by_hashing(func=lambda r: len(r.plain_text))
rule_p.output_group_config(filename_index="example/output/example-group-index-1.txt", \
    filename_groupid="example/output/example-group-id-1.txt")

# Example 2: group rules by features(overlapped)
rule_p.group_rules_by_hashing(func=lambda r: [f for f in r.involved_features])
rule_p.output_group_config(filename_index="example/output/example-group-index-2.txt", \
    filename_groupid="example/output/example-group-id-2.txt")
