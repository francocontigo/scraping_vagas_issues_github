import os
import re
from requests_html import HTMLSession
import time

def get_issues_data(url):
    s = HTMLSession()
    r = s.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        })
    issue_number = r.html.find("div.Box-row", first=True).attrs["id"]
    issue_number = re.findall(r'\d+', issue_number)
    issue_number = issue_number[0]
    r.close()
    emails = set()
    for i in range(1, int(issue_number)+1):
        r = s.get(url+str(i), headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        })
        user =r.html.find("a.author", first=True).text
        title = r.html.find("bdi.js-issue-title")[0].text
        issue_text = str(r.html.find("td.d-block", first=True).text)
        text = issue_text.lower()
        email = regex_email(issue_text)
        work_form_result = work_form(text)
        work_type_result = work_type(text)
        text_url = regex_url(text)
        description = issue_text
        r.close()
        save_data(user,title,email,work_form_result,work_type_result,text_url)
        emails.add(email)
    save_emails(emails)
        

def regex_email(text):
    email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email:
        return email[0]
    else:
        return None
        
def work_form(text):
    if "remoto" in text or "remote" in text:
        return "remote"
    elif "presencial" or "local" in text:
        return "local"
    elif "hibrido" in text or "hybrid" in text:
        return "hybrid"
    else:
        return None
        
def work_type(text):
    if "clt" in text:
        return "clt"
    elif "pj" in text:
        return "pj"
    else:
        return "ni"

def regex_url(text):
    text_url = re.findall(r'\b(https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-z]{2,})+(?:[^\s]*)?)\b', text)
    if text_url:
        return(text_url[0])
    else:
        return None

def save_emails(emails):
    directory = "data"
    output_file = "emails.txt"
    file_path = os.path.join(directory, output_file)
    
    with open(file_path, "w") as file:
        for email in emails:
            if email is not None:
                file.write(email + "\n")
            
def save_data(user,title,email,work_form_result,work_type_result,text_url):
    directory = "data"
    output_file = "data.csv"
    file_path = os.path.join(directory, output_file)
    with open(file_path, "a",  encoding="utf-8") as file:
        print(f"{user},{title},{email},{work_form_result},{work_type_result},{text_url}", file=file)

def main(url):
    get_issues_data(url)


if __name__ == "__main__":
    inicio = time.time()
    url = "https://github.com/datascience-br/vagas/issues/"
    main(url)
    fim = time.time()
    print(fim - inicio)

