
test:
	cp grades_test.csv ./grades.csv
	python hwtest.py -tm test_ex -d ./submissions -g grades.csv -a 'HW 1'

clean:
	@rm -f *.png
	@rm grades.csv grades_backup.csv grades.txt feedback.zip
	@rm -r feedback/
