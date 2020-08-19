import datetime
import requests
import re
from bs4 import BeautifulSoup


class Section:
    def __init__(self, crn, subject, course_number, section_code, title, term, reg_start_date, reg_end_date, levels, attributes, campus,
                 schedule_type, instructional_method, credits, grade_basis, comments):
        self.crn = crn
        self.subject = subject
        self.course_number = course_number
        self.section_code = section_code
        self.title = title
        self.term = term
        self.reg_start_date = reg_start_date
        self.reg_end_date = reg_end_date
        self.levels = levels
        self.attributes = attributes
        self.campus = campus
        self.schedule_type = schedule_type
        self.instructional_method = instructional_method
        self.credits = credits
        self.grade_basis = grade_basis
        self.comments = comments
        self.meetings = []

    def __str__(self):
        course_str = \
            f"crn = {self.crn}\n" \
            f"subject = {self.subject}\n" \
            f"course_number = {self.course_number}\n" \
            f"section_code = {self.section_code}\n" \
            f"title = {self.title}\n" \
            f"term = {self.term}\n" \
            f"reg_start_date = {self.reg_start_date}\n" \
            f"reg_end_date = {self.reg_end_date}\n" \
            f"levels = {self.levels}\n" \
            f"attributes = {self.attributes}\n" \
            f"campus = {self.campus}\n" \
            f"schedule_type = {self.schedule_type}\n" \
            f"instructional_method = {self.instructional_method}\n" \
            f"credits = {self.credits}\n" \
            f"grade_basis = {self.grade_basis}\n" \
            f"comments = {self.comments}\n" \
            f"=== meetings === \n"

        for meeting in self.meetings:
            course_str += str(meeting)

        return course_str


class Meeting:
    def __init__(self, type, time_start, time_end, days, location, start_date, end_date, schedule_type, instructors):
        self.type = type
        self.time_start = time_start
        self.time_end = time_end
        self.days = days
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.schedule_type = schedule_type
        self.instructors = instructors

    def __str__(self):
        return f"type = {self.type}\n" \
               f"time_start = {self.time_start}\n" \
               f"time_end = {self.time_end}\n" \
               f"days = {self.days}\n" \
               f"location = {self.location}\n" \
               f"start_date = {self.start_date}\n" \
               f"end_date = {self.end_date}\n" \
               f"schedule_type = {self.schedule_type}\n" \
               f"instructors = {self.instructors}\n"


class _SectionParser:

    ### Title info extraction helpers ###
    @staticmethod
    def __parse_title(title_html):
        title_data = title_html.text.split(" - ")

        # Correct for " - " in title
        if len(title_data) > 4:
            temp_data = []
            for i, data in enumerate(title_data):
                if i == 0:
                    temp_data.append(data)
                elif i <= len(title_data) - 4:
                    temp_data[0] += " - "
                    temp_data[0] += data
                else:
                    temp_data.append(data)
            title_data = temp_data

        return title_data

    @staticmethod
    def __get_title(title_data):
        return title_data[0]

    @staticmethod
    def __get_crn(title_data):
        return title_data[1]

    @staticmethod
    def __get_subject(title_data):
        return title_data[2].split(" ")[0]

    @staticmethod
    def __get_course_number(title_data):
        return title_data[2].split(" ")[1]

    @staticmethod
    def __get_section_code(title_data):
        return title_data[3]

    ### Detail info extraction helpers ###
    @staticmethod
    def __get_term(detail_html):
        return detail_html.find_next(text="Associated Term: ").next_element.strip()

    @staticmethod
    def __get_reg_start_date(detail_html):
        # Extract date
        reg_start_date_text = detail_html.find_next(text="Registration Dates: ").next_element.strip().split(" to ")[0]
        f = "%b %d, %Y"
        return datetime.datetime.strptime(reg_start_date_text, f).date()

        return detail_html.find_next(text="Registration Dates: ").next_element.strip()

    @staticmethod
    def __get_reg_end_date(detail_html):
        # Extract date
        reg_end_date_text = detail_html.find_next(text="Registration Dates: ").next_element.strip().split(" to ")[1]
        f = "%b %d, %Y"
        return datetime.datetime.strptime(reg_end_date_text, f).date()

    @staticmethod
    def __get_levels(detail_html):
        return detail_html.find_next(text="Levels: ").next_element.strip().split(", ")

    @staticmethod
    def __get_attributes(detail_html):
        attribute_title = detail_html.find_next(text="Attributes: ")
        # Possible for section not to have Attribute info
        if not attribute_title:
            return []
        return attribute_title.next_element.strip().split(", ")

    @staticmethod
    def __get_grade_basis(detail_html):
        return detail_html.find_next(text="Grade Basis: ").next_element.strip()

    @staticmethod
    def __get_campus(detail_html):
        return detail_html.find_next(text=re.compile("Campus$")).split("*")[0].strip()

    @staticmethod
    def __get_schedule_type(detail_html):
        return detail_html.find_next(text=re.compile("Schedule Type$")).split("*")[0].strip()

    @staticmethod
    def __get_instructional_method(detail_html):
        instructional_method = detail_html.find_next(text=re.compile("Instructional Method$"))
        # Possible for section not to have Instructional Method
        if not instructional_method:
            return None
        return instructional_method.strip()

    @staticmethod
    def __get_credits(detail_html):
        return float(detail_html.find_next(text=re.compile("Credits")).strip().split(" ")[0].strip())

    @staticmethod
    def __get_comments(detail_html):
        comments_text = detail_html.find_next(text=True).strip()
        if not comments_text:
            return None
        return comments_text

    ### Meeting info extraction helpers ###
    @staticmethod
    def __meeting_type(meeting_info):
        return meeting_info[0].text

    @staticmethod
    def __meeting_time_start(meeting_info):
        time_text = meeting_info[1].text
        if time_text == "TBA":
            return None

        # Extract time
        start_time_text = time_text.split(" - ")[0]
        f = "%I:%M %p"
        return datetime.datetime.strptime(start_time_text, f).time()

    @staticmethod
    def __meeting_time_end(meeting_info):
        time_text = meeting_info[1].text
        if time_text == "TBA":
            return None

        # Extract time
        end_time_text = time_text.split(" - ")[1]
        f = "%I:%M %p"
        return datetime.datetime.strptime(end_time_text, f).time()

    @staticmethod
    def __meeting_days(meeting_info):
        days_text = meeting_info[2].text.strip()
        if not days_text:
            return None

        return days_text

    @staticmethod
    def __meeting_location(meeting_info):
        location_text = meeting_info[3].text
        if location_text == "TBA":
            return None
        return location_text

    @staticmethod
    def __meeting_start_date(meeting_info):

        # Extract date
        start_date_text = meeting_info[4].text.split(" - ")[0]
        f = "%b %d, %Y"
        return datetime.datetime.strptime(start_date_text, f).date()

    @staticmethod
    def __meeting_end_date(meeting_info):
        # Extract date
        end_date_text = meeting_info[4].text.split(" - ")[1]
        f = "%b %d, %Y"
        return datetime.datetime.strptime(end_date_text, f).date()

    @staticmethod
    def __meeting_schedule_type(meeting_info):
        return meeting_info[5].text[:-1]

    @staticmethod
    def __meeting_instructors(meeting_info):
        # Remove multiple consecutive whitespaces
        instructors_text = re.sub(" +", " ", meeting_info[6].text)
        instructors = instructors_text.split(", ")

        # Remove "(P)" from primary instructor name
        instructors[0] = re.sub("\(P\)$", "", instructors[0])

        # Strip all instructor names
        for i, instructor in enumerate(instructors):
            instructors[i] = instructor.strip()

        return instructors

    @staticmethod
    def __parse_section(title_html, detail_html):
        # Extract title info
        title_data = _SectionParser.__parse_title(title_html)
        crn = _SectionParser.__get_crn(title_data)
        subject = _SectionParser.__get_subject(title_data)
        course_number = _SectionParser.__get_course_number(title_data)
        section_code = _SectionParser.__get_section_code(title_data)
        title = _SectionParser.__get_title(title_data)

        # Extract detail info
        term = _SectionParser.__get_term(detail_html)
        reg_start_date = _SectionParser.__get_reg_start_date(detail_html)
        reg_end_date = _SectionParser.__get_reg_end_date(detail_html)
        levels = _SectionParser.__get_levels(detail_html)
        attributes = _SectionParser.__get_attributes(detail_html)
        campus = _SectionParser.__get_campus(detail_html)
        schedule_type = _SectionParser.__get_schedule_type(detail_html)
        instructional_method = _SectionParser.__get_instructional_method(detail_html)
        credits = _SectionParser.__get_credits(detail_html)
        grade_basis = _SectionParser.__get_grade_basis(detail_html)
        comments = _SectionParser.__get_comments(detail_html)

        # Create and return section
        return Section(crn, subject, course_number, section_code, title, term,
                       reg_start_date, reg_end_date, levels, attributes, campus, schedule_type,
                       instructional_method, credits, grade_basis, comments)

    @staticmethod
    def __parse_meetings(detail_html):
        meeting_table = detail_html.find_next("table")

        meeting_info_rows = meeting_table.find_all("tr")[1:]

        meetings = []
        for meeting_info_row in meeting_info_rows:
            # Get meeting info
            meeting_info = meeting_info_row.find_all("td")

            type = _SectionParser.__meeting_type(meeting_info)
            time_start = _SectionParser.__meeting_time_start(meeting_info)
            time_end = _SectionParser.__meeting_time_end(meeting_info)
            days = _SectionParser.__meeting_days(meeting_info)
            location = _SectionParser.__meeting_location(meeting_info)
            start_date = _SectionParser.__meeting_start_date(meeting_info)
            end_date = _SectionParser.__meeting_end_date(meeting_info)
            schedule_type = _SectionParser.__meeting_schedule_type(meeting_info)
            instructors = _SectionParser.__meeting_instructors(meeting_info)

            # Create new meeting and add to list
            new_meeting = Meeting(type, time_start, time_end, days, location, start_date, end_date, schedule_type,
                                  instructors)
            meetings.append(new_meeting)

        return meetings

    @staticmethod
    def parse(page):
        soup = BeautifulSoup(page.content, 'html.parser').select(".datadisplaytable")[0]

        titles = []
        info_list = []
        for c in soup.children:
            if not c.name:
                continue

            row_child = c.select(":first-child")
            if not row_child:
                continue

            row_child = row_child[0]

            if row_child["class"][0] == "ddtitle":
                titles.append(row_child)
            elif row_child["class"][0] == "dddefault":
                info_list.append(row_child)

        sections = []
        for t, i in zip(titles, info_list):
            section = _SectionParser.__parse_section(t, i)
            section.meetings = _SectionParser.__parse_meetings(i)
            sections.append(section)

        return sections


def get_courses_for(subject, term):
    """"
    Returns list of Section objects for the given subject and term.
    Args:
        subject (str): Subject code for the Subject for which sections are being returned.
        term (str): Term code for the term for which sections are being returned.
    Returns:
        ([Section]): List of sections for given subject and given term
    """
    url = f"https://oscar.gatech.edu/pls/bprod/bwckschd.p_get_crse_unsec?term_in={term}&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj={subject}&sel_crse=&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_camp=%25&sel_ptrm=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a"
    page = requests.get(url)
    return _SectionParser.parse(page)


def get_subjects_for(term):
    """
    Returns dictionary subjects for a term.
    Args:
        term (str): Term code for the term for which subjects are being returned.
    Returns:
        (dict of str: str): Mapping subject code as key to subject name as value.
     """
    term_post_url = "https://oscar.gatech.edu/pls/bprod/bwckgens.p_proc_term_date"
    payload = {"p_calling_proc": "bwckschd.p_disp_dyn_sched", "p_term": term}
    soup = BeautifulSoup(requests.get(term_post_url, payload).content, 'html.parser')
    subject_dropdown = soup.find(id="subj_id")
    subject_options = subject_dropdown.find_all("option")
    subjects_dict = {}
    for subj in subject_options:
        subjects_dict[subj["value"]] = subj.text

    return subjects_dict


def get_available_terms():
    """
    Get dictionary of terms with available schedules.
    Args:
        None
    Returns:
        (dict of str: str): Mapping term code as key to term name as value
    """
    term_get_url = "https://oscar.gatech.edu/pls/bprod/bwckschd.p_disp_dyn_sched"
    soup = BeautifulSoup(requests.get(term_get_url).content, 'html.parser')
    term_dropdown = soup.find("select")
    term_options = term_dropdown.find_all("option")[1:]
    terms_dict = {}
    for term in term_options:
        terms_dict[term["value"]] = term.text
    return terms_dict

