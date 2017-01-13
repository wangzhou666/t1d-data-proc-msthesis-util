# rulefit-data-process-utilities

This package provides preprocessing utilities for table sheet dataset. All necessary files are placed in folder [rulefit_data_utils](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/tree/master/rulefit_data_utils).

* The module "table_processor" implements interface between in-memory data and csv table files. It also provides various methods for data manipulation that accomodates general needs. 
* The module "log_processor" implements utilities for processing specific temporal data, and output to table object.
* The module "rule_processor" implements utilities for interpreting rules generated in r package.
* The module "xlsx2csv_converter" is a tool to convert xlsx files to csv files

## Getting Started

### Prerequisites

Clone the repo:

```
git clone https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities.git
```
Make sure python and R are installed. Install corresponding depencency packages if prompted.

### Run examples

Most use cases are showed in those scripts. And you may refer to examples to design your experiments. Example scripts are placed in folder [example](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/tree/master/example). 
For simplicity, call them with [Makefile](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/blob/master/Makefile). Example may not work with Windows system, but the package does.
```
make run-example
```

To clean temporary files
```
make clean
```
## API Documents

### [table_processor](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/blob/master/rulefit_data_utils/table_processor.py)

#### Table

##### Constructors
* **Table**(filename: str, black_list: str/None, white_list: str/None)  
Create a Table with a csv file  
* **Table**(data: list[list[str]], headers: list[str], black_list: str/None, white_list: str/None)  
Create a Table with in-memory data  

##### Methods
* Table **remove_attr**(attr_name: str)  
Remove a column from Table object based on attribute name, returns itself.  
* void **write_file**(filename: str)  
Write Table object to csv file  
* Table **sort_by_attr**(primary_key: str, secondary_key: str/None)  
Sort Table object items based on key, returns itself.  
* Table **join_by_attr**(other: Table, key: str)  
Join current Table with another Table, based on given key, return new joined Table  
* Table **remove_rows_by_condition**(func: Function[Boolean])  
Remove rows based on user-defined criteria, represented by an anonymous function, function's input is a row of data, output is boolean variable, true if row should be removed, returns itself.  
* Table **horizontal_join**(other: Table)  
Join current Table with another horizontally, return new joined Table.  
*list[Table] **group_by_attr**(key: str)  
Returns a list of Table, each Table contains exactly one unique value in given column.  
* int **get_rows_num**()  
Returns total rows amount of Table.  
* int **get_cols_num**()  
Returns total columns amount of Table.  
* Table **get_cols**(cols: list[str])  
Returns new Table containing given columns from current Table.  
* Table **get_rows**(rows: list[int])  
Returns new Table containing given rows from current Table.  
* Table **remove_attr**(oldname: str, newname: str)  
Rename a column, returns itself.  
* str **get_element**(attr: str, row: int)  
Returns elements in given location of the Table.  

### [log_processor](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/blob/master/rulefit_data_utils/log_processor.py)

#### LogProcessor

This class may need more methods to accomodate future specific needs, although it works with current situations.

##### Constructor
* **LogProcessor**(source_file: str, group_key: str, black_list: str/Npne, white_list: str/None)  
Create a LogProcessor with *source_file*(longitudinal data csv file), and *group_key*(key to distinguish individuals), *black_list* and *white_list* are optional for feature selecting.  

##### Methods
* Table **flat_by_timestamp**(timestamp: str, start: int, end: int, interval: int)  
Convert coninuous temporal data with log-like records(with timestamp) to single-line vectors, returns a Table object, SUGGEST to apply to tables with "ab_zscores", "outcomes_longitudinal_mask", "tb_life_events"  
* Table **report_odds_by_timestamp**(timestamp: str, category: str, start: int, end: int, interval: int)  
Convert discret temporal data with log-like records(with timestamp) to single-line vectors, returns a Table object, SUGGEST to apply to table with "infectious_episodes_masked"  

### [rule_processor](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/blob/master/rulefit_data_utils/rule_processor.py)

#### Rule

##### Constructors
* **Rule**(text: str)
Create a Rule based on rule description generated from R package.

##### Methods
* boolean **is_matched**(row: int, data_table: Table)  
Determine whether *row*-th element in Table matchs current Rule, return True is matched, otherwise False.  

#### RuleProcessor

##### Constructors
* **RuleProcessor**(rule_description_file: str)  
Create a RuleProcessor based on rule description file generated from R package, specify file path here.  

##### Methods
* Table **get_rule_output**(data_table: Table, output_filename: str/None)  
Compute rules output given current rules, and *data_table* containing samples and features. Write to csv file if *out_filename* is not None, returns new Table with rule outputs.  
* list[Rule] **group_rules_by_hashing**(func: Function[hashable/list[hashable]])  
Group rules by user-defined hash function that returns either a hashable or list of hashable(which results in overlapped groups), return a list of grouped rules.  
* void **output_group_config**(filename_index: str, filename_groupid: str)  
Output rule groups information for SLEP package in MATLAB  
* RuleProcessor **remove_rules_by_condition**(func: Function[Boolean])  
Remove rules satisfying user-defined criteria, return RuleProcessor itself.  
* RuleProcessor **add_rule_by_text**(text: str)
Add a new rule to current rule processor, return it self.

### [xlsx2csv_converter](https://github.tamu.edu/Wangzhou123/rulefit-data-process-utilities/blob/master/rulefit_data_utils/xlsx2csv_converter.py)

#### Xlsx2CsvConverter

##### Constructors

* **Xlsx2CsvConverter**(xlsxdir: str, csvdir: str)  
Create Xlsx2CsvConverter based on source directory containing all xlsx file, and target directory to place csv files.  

##### Methods
* void **conver**()  
Output csv files to configured location.


