import os
import re
from requests_html import HTMLSession
import time
from joblib import Parallel, delayed

class DataProcessor:
    """
    A class for processing data from GitHub issues related to job vacancies.
    """

    def __init__(self, url):
        """
        Initializes a DataProcessor object.

        Parameters:
            url (str): The URL of the GitHub issues page.
        """
        self.directory = "data"
        self.output_file_csv = "data.csv"
        self.file_path_csv = os.path.join(self.directory, self.output_file_csv)
        self.output_file_email = "emails.txt"
        self.file_path_email = os.path.join(self.directory, self.output_file_email)
        self.url = url
        self.session = HTMLSession()

    def get_issue_number(self):
        """
        Retrieves the total number of issues from the GitHub page.

        Returns:
            int: The total number of issues.
        """
        r = self.session.get(self.url, headers=self.get_headers())
        issue_number = r.html.find("div.Box-row", first=True).attrs["id"]
        issue_number = re.findall(r'\d+', issue_number)
        r.close()
        return int(issue_number[0]) if issue_number else 0

    def process_issue(self, issue_number):
        """
        Processes information from a specific GitHub issue.

        Parameters:
            issue_number (int): The number of the GitHub issue to process.
        """
        issue_url = f"{self.url}{issue_number}"
        r = self.session.get(issue_url, headers=self.get_headers())
        user = r.html.find("a.author", first=True).text
        title = r.html.find("bdi.js-issue-title")[0].text
        issue_text = str(r.html.find("td.d-block", first=True).text)
        text = issue_text.lower()
        email = self.regex_email(issue_text)
        work_form_result = self.work_form(text)
        work_type_result = self.work_type(text)
        text_url = self.regex_url(text)
        r.close()
        self.save_data(user, title, email, work_form_result, work_type_result, text_url)

    def process_issues_data(self):
        """
        Processes information from each GitHub issue, utilizing parallel processing for efficiency.

        This method retrieves the total number of GitHub issues, and then employs parallel processing to
        imultaneously process information from each issue. The processed data is then saved.
        """
        issue_number = self.get_issue_number()

        def process_single_issue(i):
            self.process_issue(i)
        Parallel(n_jobs=-1)(delayed(process_single_issue)(i) for i in range(1, issue_number + 1))

    def regex_email(self, text):
        """
        Extracts email addresses from the given text using regular expressions.

        Parameters:
            text (str): The text to search for email addresses.

        Returns:
            str: The extracted email address or None if not found.
        """
        email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return email[0] if email else None

    def work_form(self, text):
        """
        Determines the work form (remote, local, hybrid) based on the given text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            str or None: The determined work form or None if not identified.
        """
        if "remoto" in text or "remote" in text:
            return "remote"
        elif "presencial" in text or "local" in text:
            return "local"
        elif "hibrido" in text or "hybrid" in text:
            return "hybrid"
        else:
            return None

    def work_type(self, text):
        """
        Determines the work type (CLT, PJ, NI) based on the given text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            str: The determined work type.
        """
        if "clt" in text:
            return "clt"
        elif "pj" in text:
            return "pj"
        else:
            return "ni"

    def regex_url(self, text):
        """
        Extracts URLs from the given text using regular expressions.

        Parameters:
            text (str): The text to search for URLs.

        Returns:
            str or None: The extracted URL or None if not found.
        """
        text_url = re.findall(r'\b(https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-z]{2,})+(?:[^\s]*)?)\b', text)
        return text_url[0] if text_url else None

    def save_data(self, user, title, email, work_form_result, work_type_result, text_url):
        """
        Saves processed data to a CSV file.

        Parameters:
            user (str): The author of the GitHub issue.
            title (str): The title of the GitHub issue.
            email (str): The extracted email address.
            work_form_result (str or None): The determined work form.
            work_type_result (str): The determined work type.
            text_url (str or None): The extracted URL.
        """
        
        if email:
            with open(self.file_path_email, "a", encoding="utf-8") as file:
                print(f"{email}", file=file)
        
        with open(self.file_path_csv, "a", encoding="utf-8") as file:
            print(f"{user},{title},{email},{work_form_result},{work_type_result},{text_url}", file=file)

    def get_headers(self):
        """
        Returns headers for HTTP requests.

        Returns:
            dict: The headers.
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

    def clean_local_data(self):  
        with open(self.file_path_csv, "w", encoding="utf-8") as file:
            print(f"user,title,email,work_form_result,work_type_result,text_url", file=file)

        with open(self.file_path_email, "w", encoding="utf-8"):
            print("")

    def clean_email_duplicates(self):
        emails = set()
        
        for line in open(self.file_path_email):
            emails.add(line)
        with open(self.file_path_email, "w") as file:
            for email in emails:
                    file.write(email)
            

def main():
    """
    The main function that initiates the data processing and measures the time taken.
    """
    url = "https://github.com/datascience-br/vagas/issues/"
    data_processor = DataProcessor(url)

    inicio = time.time()
    data_processor.clean_local_data()
    data_processor.process_issues_data()
    data_processor.clean_email_duplicates()
    fim = time.time()
    print(f"Time taken: {fim - inicio} seconds")

if __name__ == "__main__":
    main()

