import os
import re
from requests_html import HTMLSession
import time

class DataProcessor:
    def __init__(self, url):
        self.url = url
        self.session = HTMLSession()
        self.emails = set()

    def get_issue_number(self):
        r = self.session.get(self.url, headers=self.get_headers())
        issue_number = r.html.find("div.Box-row", first=True).attrs["id"]
        issue_number = re.findall(r'\d+', issue_number)
        r.close()
        return int(issue_number[0]) if issue_number else 0

    def process_issue(self, issue_number):
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
        self.emails.add(email) if email else None

    def process_issues_data(self):
        issue_number = self.get_issue_number()
        for i in range(1, issue_number + 1):
            self.process_issue(i)
        self.save_emails()

    def regex_email(self, text):
        email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return email[0] if email else None

    def work_form(self, text):
        if "remoto" in text or "remote" in text:
            return "remote"
        elif "presencial" in text or "local" in text:
            return "local"
        elif "hibrido" in text or "hybrid" in text:
            return "hybrid"
        else:
            return None

    def work_type(self, text):
        if "clt" in text:
            return "clt"
        elif "pj" in text:
            return "pj"
        else:
            return "ni"

    def regex_url(self, text):
        text_url = re.findall(r'\b(https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-z]{2,})+(?:[^\s]*)?)\b', text)
        return text_url[0] if text_url else None

    def save_emails(self):
        directory = "data"
        output_file = "emails.txt"
        file_path = os.path.join(directory, output_file)

        with open(file_path, "w") as file:
            for email in self.emails:
                if email:
                    file.write(email + "\n")

    def save_data(self, user, title, email, work_form_result, work_type_result, text_url):
        directory = "data"
        output_file = "data.csv"
        file_path = os.path.join(directory, output_file)

        with open(file_path, "a", encoding="utf-8") as file:
            print(f"{user},{title},{email},{work_form_result},{work_type_result},{text_url}", file=file)

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

def main():
    url = "https://github.com/datascience-br/vagas/issues/"
    data_processor = DataProcessor(url)

    inicio = time.time()
    data_processor.process_issues_data()
    fim = time.time()

    print(f"Time taken: {fim - inicio} seconds")

if __name__ == "__main__":
    main()
