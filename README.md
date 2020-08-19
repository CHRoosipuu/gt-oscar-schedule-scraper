# GT Schedule Scraper

GT Schedule Scraper is a Python3 module for scraping the Georgia Tech course schedule from https://oscar.gatech.edu/pls/bprod/bwckgens.p_proc_term_date.

## Installation

To use the module simply download ```gt_schedule_scraper.py``` and place it in your project directory.

## Requirements

* Python 3.6 or greater
* requests
* bs4

## Usage

```python
import gt_schedule_scraper as gtss

gtss.get_available_terms() # returns dict of terms (semesters) {key: term code, value: term name}

term_code = "202008" # term code for Fall 2020
gtss.get_subjects_for(term_code) # returns dict of subjects for given term {key: subject code, value: subject name}

subject_code = "ACCT" # subject code for Accounting
gtss.get_courses_for(subject_code, term_code) # returns list of sections for given term and subject as Section objects

```

### Section Class

Class to represent course section.

```python
section.crn # (int)
section.subject # (str)
section.course_number # (int)
section.section_code # (str)
section.title # (str)
section.term # (str)
section.reg_start_date # (datetime.date)
section.reg_end_date # (datetime.date)
section.levels # (str[])
section.attributes # (str[])
section.campus # (str)
section.schedule_type # (str)
section.instructional_method # (str)
section.credits # (float)
section.grade_basis # (str)
section.comments # (str)
section.meetings # (Meeting[])
```

### Meeting Class

Class to represent section meeting.

```python
meeting.type # (str)
meeting.time_start # (datetime.time)
meeting.time_end # (datetime.time)
meeting.days # (str)
meeting.location # (str)
meeting.start_date # (datetime.date)
meeting.end_date # (datetime.date)
meeting.schedule_type # (str)
meeting.instructors # (str[])
```