from rulefit_data_utils import table_processor as tp
from rulefit_data_utils import log_processor as lp
from rulefit_data_utils import rule_processor as rp

########## log processor ################

logs1 = lp.LogProcessor(source_file="data/csv/mp88_outcomes_longitudinal_mask.csv", \
    group_key="Mask Id", \
    white_list="example/tmp/example-white-list.txt")
logs2 = lp.LogProcessor(source_file="data/csv/mp88_infectious_episodes_masked.csv", \
    group_key="Mask Id")

table_outcome_longitudinal = logs1.flat_by_timestamp(timestamp="Due_num", start=0, end=30, interval=3)
table_infec_episodes = logs2.report_odds_by_timestamp(timestamp='Inf Age Mos', category='Inf Epi Group', start=0, end=30, interval=3)

########### table processor ##############

# read csv to table object, can use black_list or white_list to specify acceptable features

# allowing all attributes this time
table1 = tp.Table(filename="data/csv/mp88_infectious_episodes_masked.csv") 
# use black list to filter attributes
table2 = tp.Table(filename="data/csv/mp88_baseline_variables_masked.csv", \
    black_list="example/tmp/example-black-list.txt")
# use white list to filter attributes
table3 = tp.Table(filename="data/csv/mp88_outcomes_longitudinal_mask.csv", \
    white_list="example/tmp/example-white-list.txt") # use white list to filter attributes

# remove rows whose first elements starts with '2'
# can use this to select samples
table2.remove_rows_by_condition(func=lambda x: x[0][0] == '2' if len(x[0]) > 0 else False)

# remove column with attribute 'Work 2'
# can use this to select features
table2.remove_attr('Work 2')

# sort table2 by mask id
table2.sort_by_attr(primary_key="Mask Id")

# get mask id value of 8th sample in table2
print table2.get_element(attr="Mask Id", row=8)

# join baseline features with infectious record feature and flatted longitudinal features
table_joined = table2.join_by_attr(table_outcome_longitudinal, key="Mask Id")
table_joined = table_joined.join_by_attr(table_infec_episodes, key="Mask Id")

table_joined.sort_by_attr(primary_key="Mask Id").write_file("example/output/example-processed-data.csv")

##############################

table_feature = tp.Table(filename="example/output/example-processed-data.csv")
# find labels by joining longitudinal table, because the "T1D" labels are there
# use sort_by_attr to guarantee two table items are in the same order
table_label = table_feature.join_by_attr(\
    tp.Table(filename="data/csv/mp88_outcomes_longitudinal_mask.csv"), \
    key="Mask Id")\
    .sort_by_attr(primary_key="Mask Id")\
    .get_cols(cols=["T1D"])

table_feature.sort_by_attr(primary_key="Mask Id")\
    .remove_attr("Mask Id")\
    .write_file("example/output/example-features.csv")
table_label.write_file("example/output/example-labels.csv")

print "then run get_rules.r with R, to get rules"


