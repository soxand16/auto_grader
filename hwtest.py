import unittest
import re
import sys
import argparse
import importlib
import os
import shutil
import zipfile
import csv
import signal
import numpy as np
import matplotlib.pyplot as plt
from sys import platform
import multiprocessing as mp


class StudentTestLoader(unittest.TestLoader):
       
    def loadTestsFromTestCase(self, testCaseClass, **kwargs):
        """Return a suite of all tests cases contained in testCaseClass."""
        testCaseNames = self.getTestCaseNames(testCaseClass)
        testCases = []
        for testCaseName in testCaseNames:
            testCases.append(testCaseClass(testCaseName, **kwargs))
        loadedSuite = self.suiteClass(testCases)
        return loadedSuite

class StudentRunner:
    """Run the TestCase for a student module.
    """

    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def writeUpdate(self, message):
        self.stream.write(message)

    def run(self, test, mod):
        """ Run the given test case or test suite.  """
        result = StudentTestResult(self)
        # The following updates will be written in the terminal
        self.writeUpdate("*"*70+"\n")
        self.writeUpdate("STUDENT: " + mod.__name__+"\n")
        test(result)
        result.process()
        self.writeUpdate("TOTAL: {}\n".format(result.data['total']))
        self.writeUpdate("SCORE: {}\n".format(result.data['score']))
        self.writeUpdate("~"*70+"\n\n")
        return result

class StudentTestResult(unittest.TestResult):

    def __init__(self, runner):
        unittest.TestResult.__init__(self)
        self.runner = runner
        self.data = {}
        self.data['tests'] = {}

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)

        # extract points
        points = re.findall(r'(?<=points=)\d+', test._testMethodDoc)
        if not points :
            points = 1
        else :
            points = int(points[0])
            
        self.runner.writeUpdate('{0}, {1}, {2} '.format(test._testMethodName, points, test.shortDescription()))
        self.data['tests'][test._testMethodName] = {}
        self.data['tests'][test._testMethodName]['points'] = points
        self.data['tests'][test._testMethodName]['description'] = test.shortDescription()
        
    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self.data['tests'][test._testMethodName]['status'] = 'pass'
        self.runner.writeUpdate('PASS\n')

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.data['tests'][test._testMethodName]['status'] = 'error'
        self.runner.writeUpdate('ERROR\n')

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.data['tests'][test._testMethodName]['status'] = 'failure'
        self.runner.writeUpdate('FAIL\n')

    def process(self):
        
        # add the raw messages from exceptions due to errors
        for test, raw in self.errors:
            self.data['tests'][test._testMethodName]['raw'] = raw
        # do the same for exceptions raided from test failures
        for test, raw in self.failures:
            self.data['tests'][test._testMethodName]['raw'] = raw
            # extract the short message from failed test for delivery
            # to the student
            msg_idx = raw.rfind(':')
            if msg_idx > -1:
                self.data['tests'][test._testMethodName]['message'] = raw[msg_idx+2:]
        # compute total points
        score = 0
        total = 0
        for test in self.data['tests'].keys():
            points = self.data['tests'][test]['points']
            total += points
            if self.data['tests'][test]['status'] == 'pass':
                score += points
        self.data['score'] = score
        self.data['total'] = total
        self.data['percent'] = 100*score/total
        
class timeout:
    """ 
    Class designed to handle infinite while loops. Returns TimeoutError 
    after the specified time
    """
    def __init__(self, seconds=5, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)
        
class HWTestBase(unittest.TestCase):
    """
    Base class for tests to be imported to tester
    """
    
    def __init__(self, testname, module):
        super().__init__(testname)
        self.module = module
        
               
def runTests(name, test_class):
    """
    Runs tests in test class for all of the filename 'name'
    
    Arguments :
        names : str
            str of filename to be tested
        test_class : HWTestBase class
            class based on HWTestBase containing tests to be run
            
    Returns :
        data : dict
            dictionairy with name as key to dictionary containing
            test results
    """
    
    data = {}
    print("Testing ", name)
    data[name] = {}
    if platform in ['win32', 'win64'] :
        print("I'm on Windoze and can't use signal!!!")
    try:
        with timeout(seconds=10) :
            mod = importlib.import_module(name)
    except TimeoutError :
        data[name]['total'] = 0
        data[name]['percent'] = 0
        data[name]['comment'] = 'Likely an infinite while loop!'
        print("Likely an infinite while loop!\n")
    except:
        data[name]['total'] = 0
        data[name]['percent'] = 0
        data[name]['comment'] = 'Importing led to an error.'
        print("importing led to an error!\n")
    else:
        try:
            loader = StudentTestLoader()
            suite = loader.loadTestsFromTestCase(test_class, module=mod)
            result = StudentRunner().run(suite, mod)
            data[name] = result.data
        except:
            print("test suite failed!")
    return data

def gradingStatistics(data) :
    """
    Counts numper of passes, failures, and errors for each test
    
    Arguments : 
        data : dict
            dictionary containing dictionaries for each files test results
            
    Returns: 
        stats : dict
            dictionary containing dictionary of passes, failures, and errors
            for each test
    """
    
    # initializes the stats dictionary for each test
    stats = {}
    i = 0
    name = list(data.keys())[i]
    while not 'tests' in data[name].keys() :
        i += 1
        name = list(data.keys())[i]        
    for test in data[name]['tests'] :
        stats[test] = {'pass':0, 'failure': 0, 'error': 0, 'total':0}
        
    # fills in data from tests    
    for name in data.keys() :
        if 'tests' in data[name].keys() :
            for test in data[name]['tests'] :
                test_status = data[name]['tests'][test]['status']
                stats[test][test_status] += 1
                stats[test]['total'] += 1

    return stats

def plotStats(stats) :
    """
    Creates a stacked bar plot to visualize performance on each test
    
    Arguments :
        stats : dict
            dictionary containing dictionary of passes, failures, and errors
            for each test
            
    Creates :
        stats_plot.png : .png file
            graphic representation of performance by test
    """
    
    xticklabels = []
    passes = np.array([])
    fails = np.array([])
    errors = np.array([])
    totals = np.array([])
    
    # Appends each test name to xticklabels and makes arrays of the data
    for test in stats.keys() :
        xticklabels.append(test)
        passes = np.append(passes, stats[test]['pass'])
        fails = np.append(fails, stats[test]['failure'])
        errors = np.append(errors, stats[test]['error'])
        totals = np.append(totals, stats[test]['total'])
    
    # Normalizes the data by percentage
    passes = passes*100/totals
    fails = fails*100/totals
    errors = errors*100/totals
    
    # Graph formatting
    ind = np.arange(0, len(xticklabels)*2, 2)
    width = 0.25
    
    # Plotting
    plt.figure(figsize=(10,6), edgecolor='w')    
    p1 = plt.barh(ind, passes, width, color=(0.41, 1.0, 0.62))
    p2 = plt.barh(ind, fails, width, color=(1.0, 0.5, 0.62), left=passes)
    p3 = plt.barh(ind, errors, width, color=(0.2588,0.4433,1.0), left=passes+fails)
    
    # Label and title
    plt.xlabel('Percent')
    plt.title('Grading Statistics', loc='left')
    
    # axis ticks and legend and layout
    plt.yticks(ind, xticklabels, rotation='horizontal')
    plt.xticks(np.arange(0,101, 10), rotation='horizontal')
    plt.legend((p1[0], p2[0], p3[0]), ('Passes', 'Failures', 'Errors'), bbox_to_anchor=(1,1.06), loc='upper right',
               ncol=3, borderaxespad=0.)
    plt.tight_layout()
    
    # saves figure
    plt.savefig('stats_plot.png')  
    
    
def processResults(data, naughty, modified, directory) :
    
    f = open('grades.txt', 'w')
    for name in data.keys() :
        f.write('-'*70 + '\n')
        f.write(name + '\n\n')
        try :    
            for test in data[name]['tests'] :
                #f.write(test + '\n')
                f.write('TEST DESCRIPTION: ' + data[name]['tests'][test]['description'] + '\n')
                f.write('POINTS: {}'.format(data[name]['tests'][test]['points']) + '\n')
                f.write('STATUS: ' + data[name]['tests'][test]['status'] + '\n') 
                if 'message' in data[name]['tests'][test]:
                    f.write('FEEDBACK: ' + data[name]['tests'][test]['message'] + '\n')
                elif data[name]['tests'][test]['status'] == 'error' :
                    f.write('RAW ERROR OUTPUT:\n' + data[name]['tests'][test]['raw']+'\n')
                else:
                    f.write('\n')
        except :
            f.write(data[name]['comment'] + '\n\n')

        f.write('TOTAL % FROM TESTS: {:.2f}\n'.format(data[name]['percent']))
        if name in naughty :
            f.write('PENALTY: ' + naughty[name] + '\n')
            f.write('ADJUSTED TOTAL: {:.2f}\n'.format(max([data[name]['percent'] - 20.0, 0])))            
            
        f.write('\n' + '*'*70 + '\n')
    
    f.close()
    # delete the modified file    
    for name in modified.keys() :
        os.remove(directory+'/'+name+'.py')
        
def splitResults(modified) :
    """Splits all results and overwrites the origal files with feedback to 
    be zipped and reuploaded to canvas.
    
    Args:
        directory - path to directory containing the submissions   
    """
    
    #creates the feedback directory if it doesn't exist
    if not os.path.exists('./feedback') :
        os.makedirs('./feedback')
        
    #opens the already written grades file
    f = open('grades.txt', 'r')    
    #seperates the feedback for each student and stores in an array
    feedback_array = f.read()[71:-72].split('*'*70+'\n'+'-'*70+'\n')
    #close file
    f.close()
    
    for feedback in feedback_array :
        #get submitted file name
        filename = modified[feedback[:feedback.index('\n')]]
        #open file in feedback folder and write feedback into it
        f = open('./feedback/' + filename + '.py', 'w')
        f.write(feedback)
        f.close()
    # zips file    
    zipf = zipfile.ZipFile('feedback.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk('./feedback') :
        for file in files :
            zipf.write(os.path.join(root, file))
    zipf.close()
    
def updateGrades(grades_file, assignment, studentID) :
    """Updates the grades csv with the scores from testing
    
    Args:
        grades_file - name of csv file of gradebook downloaded from canvas
    """
    shutil.copyfile(grades_file, 'grades_backup.csv')
    #opens csv files
    csvfilein = csv.reader(open('grades_backup.csv', 'r'))
    csvfileout = csv.writer(open(grades_file, 'w'))
    
    #gets header
    headers = csvfilein.__next__()
    #gets the index of the assignment for grade updates
    canvas_assignment = [string for string in headers if re.match(assignment+' \(\d+\)', string)]
    index = headers.index(canvas_assignment[0])
    
    csvfileout.writerow(headers[:5]+headers[index:index+1])
    
    #next line is whether assignment is muted or not
    #preserved for all other assignments, assignment being graded muted for review on upload
    muted = csvfilein.__next__()
    muted[index] = 'Muted'
    csvfileout.writerow(muted[:5]+muted[index:index+1])
    
    #next line is points for an assignment
    #gets value of total points and stores for future use
    #copies over to new csv
    points = csvfilein.__next__()
    assignment_points = points[index]
    csvfileout.writerow(points[:5]+points[index:index+1])
    
    for row in csvfilein :
        # name of student file for student with the ID contained in row
        if row[1] in studentID :
            name = studentID[row[1]]
            # calcualtes score
            score = float(data[name]['percent'])*float(assignment_points)/100
            # updates score and writes to new csv
            row[index] = score
        else :
            print(row[0] + ' had no submission for this assigment.')
            
        csvfileout.writerow(row[:5]+row[index:index+1])
        
    
                    
def cleanup_filename(filename) :
    """Checks files for characters that make the file unable to be imported
    as a module and removes those characters from the filename so tests can
    be run"""
    original = filename
    change = ''
    if re.search("-\d+", filename) :
        #Gets rid of canvas added -\d at end of file
        filename = re.sub("-\d+", "", filename)
    if '-' in filename :
        # Gets rid of dashes
        filename = filename.replace('-','_') 
        change += '-'
    if '#' in filename :
        # Gets rid of pound sign (some students put 'hw#4' in their name)
        filename = filename.replace('#','')  
        change += '#'
    if '+' in filename :
        # Gets rid of pound sign (some students put 'hw#4' in their name)
        filename = filename.replace('+','')  
        change += '+'
    if ' ' in filename :
        # Gets rid of pound sign (some students put 'hw#4' in their name)
        filename = filename.replace(' ','_')  
        change += ' '
    if '.' in filename[:-3] :
        # Swithches periods to underscores since some students use them in 
        # place of them. Does not replace the '.' in '.py'
        filename = filename[:-3].replace('.', '_') + filename[-3:]
        change += '.'
    return filename, original, change 

def load_names(pattern, exclude, directory):
    """ Get all the matching module names (possibly modified).
    
    Args:
        pattern - regex pattern that matches submissions
        exclude - regex pattern that matches files not to be included
        directory - path to directory containing the submissions
    Returns:
        names - list of strings representing modules to be tested
        naughty - dictionary of name/message pairs, where the name is
                  a file that had bad symbols (i.e., directions were not
                  followed)
        modified - dictionary of name/location pairs where location
                   is the modified file produced during filtering
    """
    
    names = []
    naughty = {} 
    modified = {}
    studentID = {}
    
    for filename in os.listdir(directory):
        
        # First, clean up the filename by removing bad symbols.  This
        # assumes that submissions won't have weird prefixes placed on them
        # by Canvas that inject other symbols.  Maybe there is a way to 
        # get the files as named upon submission?
        filename, original, change = cleanup_filename(filename)
        
        # If the filename as cleaned is not excluded, check if it matches
        # the pattern given by the caller.
        if not re.search(exclude, filename) and re.search(pattern, filename): 
            
            # Modify the file name if it matched.
            newname = re.search(pattern, filename).group()
            #makes student ID number key to new file name
            if not re.search('late', filename) :
                studentID[filename.split('_')[1]] = newname[:-3]
            else :
                studentID[filename.split('_')[2]] = newname[:-3]
            # Continue only if the name of the module is not already
            # in the list of names.  This should almost always be true, but
            # certain testing might leave junk in the folder.
            if newname[:-3] not in names: 
                
                names.append(newname[:-3]) # remove .py
                if change :
                    naughty[newname[:-3]] = \
                        "Submitted file name contained one or more of the following: " + change

            if newname != original:
                modified[newname[:-3]] = original[:-3]
                shutil.copyfile(directory + '/' + original, directory + '/' + newname)

    return names, naughty, modified, studentID

if __name__ == "__main__":
    # Set up parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-tm", "--test_module", help="module containing test class",
                        default="test_ex")
    parser.add_argument("-tc", "--test_class", help="name of test class",
                        default="TestHW")
    parser.add_argument("-s", "--single", help="name of single module to test",
                        default=None)
    parser.add_argument("-p", "--pattern", help="regex pattern to be matched by tested modules",
                        default="[A-Za-z]+_[A-Za-z]+_(?i)h(?i)w\d+.py")
    parser.add_argument("-e", "--exclude", help="regex pattern to be excluded by tested modules",
                        default=r"test|solution|definition")
    parser.add_argument("-d", "--directory", help="directory with submissions to be tested",
                        default="./")
    parser.add_argument("-g", "--grades_file", help="csv of canvas gradebook",
                        default=None)
    parser.add_argument("-a", "--assignment", help="string of the asignment name in canvas",
                        default=None)
    parser.add_argument("-o", "--open_stats", help="bool, True opens stats_plot at end of testing",
                        default=False)
    args = parser.parse_args()    
    
    # add directory to path
    sys.path.append(args.directory)
    
    # import test class
    try:
        tm = importlib.import_module(args.test_module)
        tc = getattr(tm, args.test_class)
    except:
        print("Error importing " + args.test_class + " from " + args.test_module)
    else:
        # if single file to test
        if args.single :
            names = [args.single]
            naughty = {}
            modified = {}
        else:
            # get the names through file filtering
            names, naughty, modified, studentID = load_names(args.pattern, args.exclude, args.directory)
        # Parallization of testing
        pool = mp.Pool(processes=4)
        data_list = [pool.apply(runTests, args=(name,tc)) for name in names] 
        data = {}
        for result in data_list :
            data = {**data, **result}
        stats = gradingStatistics(data)
        processResults(data, naughty, modified, args.directory)
        if not args.single :
            splitResults(modified)
            if args.grades_file and args.assignment:
                updateGrades(args.grades_file, args.assignment, studentID)
            else :
                print('pass the assignment name and csv of canvas grade book to produce an updated grades csv')
        plotStats(stats)
        if args.open_stats :
            os.system('open stats_plot.png')
            