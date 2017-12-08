# Automatic Grading Program

This program is designed to cutdown on time spent grading student submissions by automating the process using unittest framework.

## File Usage

usage: hwtest.py [-h] [-tm TEST_MODULE] [-tc TEST_CLASS] [-s SINGLE]
[-p PATTERN] [-e EXCLUDE] [-d DIRECTORY] [-g GRADES_FILE]
[-a ASSIGNMENT] [-o OPEN_STATS] [-pr PROCESSES]

optional arguments:

    -h, --help            show this help message and exit

    -tm TEST_MODULE, --test_module TEST_MODULE
    module containing test class, default="test_ex"
    
    -tc TEST_CLASS, --test_class TEST_CLASS
    name of test class, default="TestHW"
    
    -s SINGLE, --single SINGLE
    name of single module to test, default=None
    
    -p PATTERN, --pattern PATTERN
    regex pattern to be matched by tested modules, default="[A-Za-z]+_[A-Za-z]+_(?i)h(?i)w\d+.py"
    
    -e EXCLUDE, --exclude EXCLUDE
    regex pattern to be excluded by tested modules, default=r"test|solution|definition"
    
    -d DIRECTORY, --directory DIRECTORY
    directory with submissions to be tested, default="./submissions"
    
    -g GRADES_FILE, --grades_file GRADES_FILE
    csv of canvas gradebook, default=None
    
    -a ASSIGNMENT, --assignment ASSIGNMENT
    string of the asignment name in canvas, default=None
    
    -o OPEN_STATS, --open_stats OPEN_STATS
    bool, True opens stats_plot at end of testing, default=False
    
    -pr PROCESSES, --processes PROCESSES
    number of parallel processes, default=4
