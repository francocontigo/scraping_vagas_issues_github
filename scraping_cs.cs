using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Text.RegularExpressions;

namespace GitHubIssueProcessor
{
    class DataProcessor
    {
        private string url;
        private HttpClient client;
        private HashSet<string> emails;

        public DataProcessor(string url)
        {
            this.url = url;
            this.client = new HttpClient();
            this.emails = new HashSet<string>();
        }

        public void ProcessIssuesData()
        {
            int issueNumber = GetIssueNumber();
            for (int i = 1; i <= issueNumber; i++)
            {
                ProcessIssue(i);
            }
            SaveEmails();
        }

        private int GetIssueNumber()
        {
            HttpResponseMessage response = client.GetAsync(url).Result;
            string content = response.Content.ReadAsStringAsync().Result;

            string pattern = @"<div class=""Box-row"" id=""issue_([\d]+)"">";
            Match match = Regex.Match(content, pattern);

            response.Dispose();

            return match.Success ? int.Parse(match.Groups[1].Value) : 0;
        }

        private void ProcessIssue(int issueNumber)
        {
            string issueUrl = $"{url}{issueNumber}";
            HttpResponseMessage response = client.GetAsync(issueUrl).Result;
            string content = response.Content.ReadAsStringAsync().Result;

            string userPattern = @"<a[^>]+class=""author""[^>]*>([^<]+)</a>";
            string titlePattern = @"<bdi class=""js-issue-title"">([^<]+)</bdi>";
            string textPattern = @"<td[^>]+class=""d-block""[^>]*>([^<]+)</td>";

            string user = Regex.Match(content, userPattern).Groups[1].Value;
            string title = Regex.Match(content, titlePattern).Groups[1].Value;
            string issueText = Regex.Match(content, textPattern).Groups[1].Value;
            string text = issueText.ToLower();

            string email = RegexEmail(issueText);
            string workFormResult = WorkForm(text);
            string workTypeResult = WorkType(text);
            string textUrl = RegexUrl(text);

            response.Dispose();

            SaveData(user, title, email, workFormResult, workTypeResult, textUrl);

            if (email != null)
            {
                emails.Add(email);
            }
        }

        private string RegexEmail(string text)
        {
            string pattern = @"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}";
            Match match = Regex.Match(text, pattern);
            return match.Success ? match.Value : null;
        }

        private string WorkForm(string text)
        {
            if (text.Contains("remoto") || text.Contains("remote"))
            {
                return "remote";
            }
            else if (text.Contains("presencial") || text.Contains("local"))
            {
                return "local";
            }
            else if (text.Contains("hibrido") || text.Contains("hybrid"))
            {
                return "hybrid";
            }
            else
            {
                return null;
            }
        }

        private string WorkType(string text)
        {
            if (text.Contains("clt"))
            {
                return "clt";
            }
            else if (text.Contains("pj"))
            {
                return "pj";
            }
            else
            {
                return "ni";
            }
        }

        private string RegexUrl(string text)
        {
            string pattern = @"\b(https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-z]{2,})+(?:[^\s]*)?)\b";
            Match match = Regex.Match(text, pattern);
            return match.Success ? match.Value : null;
        }

        private void SaveEmails()
        {
            string directory = "data";
            string outputFileName = "emails.txt";
            string filePath = Path.Combine(directory, outputFileName);

            using (StreamWriter file = new StreamWriter(filePath))
            {
                foreach (string email in emails)
                {
                    if (email != null)
                    {
                        file.WriteLine(email);
                    }
                }
            }
        }

        private void SaveData(string user, string title, string email, string workFormResult, string workTypeResult, string textUrl)
        {
            string directory = "data";
            string outputFileName = "data.csv";
            string filePath = Path.Combine(directory, outputFileName);

            using (StreamWriter file = new StreamWriter(filePath, true, System.Text.Encoding.UTF8))
            {
                file.WriteLine($"{user},{title},{email},{workFormResult},{workTypeResult},{textUrl}");
            }
        }
    }

    class Program
    {
        static void Main()
        {
            string url = "https://github.com/datascience-br/vagas/issues/";
            DataProcessor dataProcessor = new DataProcessor(url);

            DateTime start = DateTime.Now;
            dataProcessor.ProcessIssuesData();
            DateTime end = DateTime.Now;

            Console.WriteLine($"Time taken: {(end - start).TotalSeconds} seconds");
        }
    }
}
