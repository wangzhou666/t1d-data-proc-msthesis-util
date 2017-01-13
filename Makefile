clean:
	rm data/csv/*
	rm rulefit_data_utils/*.pyc
	rm example/output/*

run-example:
	if [ ! -d data/csv ]; then mkdir data/csv; fi 
	python example/xlsx2csv.py
	python example/basic_operations.py
	Rscript example/get_rules.r
	python example/rule_output.py