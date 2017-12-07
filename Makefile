
test:
	cp grades_test.csv ./grades.csv
	python hwtest.py -tm test_ex -d ./submissions -g grades.csv -a 'HW 1'

time_parallels:
	@cp grades_test.csv ./grades.csv
	@echo 'Testing 1 process'
	@time python hwtest.py -tm test_ex -d ./submissions -g grades.csv -a 'HW 1' -pr 1
	@cp grades_test.csv ./grades.csv
	@echo 'Testing 2 process'
	@time python hwtest.py -tm test_ex -d ./submissions -g grades.csv -a 'HW 1' -pr 2
	@cp grades_test.csv ./grades.csv
	@echo 'Testing 3 process'
	@time python hwtest.py -tm test_ex -d ./submissions -g grades.csv -a 'HW 1' -pr 3
	@cp grades_test.csv ./grades.csv
	@echo 'Testing 4 process'
	@time python hwtest.py -tm test_ex -d ./submissions -g grades.csv -a 'HW 1' -pr 4


clean:
	@rm -f *.png
	@rm grades.csv grades_backup.csv grades.txt feedback.zip
	@rm -r feedback/
