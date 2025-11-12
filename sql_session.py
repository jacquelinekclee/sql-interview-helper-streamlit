import requests
from bs4 import BeautifulSoup 
import numpy as np
import openai

class SQLSession:
    
    w3_sql_topic_urls = {'Retrieve data from tables': ['https://www.w3resource.com/sql-exercises/sql-retrieve-exercise-{}.php', range(1, 34)],
                         'Boolean and Relational Operators': ['https://www.w3resource.com/sql-exercises/sql-boolean-operator-exercise-{}.php', range(1, 13)],
                         'Wildcard and Special operators': ['https://www.w3resource.com/sql-exercises/sql-wildcard-special-operator-exercise-{}.php', range(1, 23)],
                         'Aggregate Functions': ['https://www.w3resource.com/sql-exercises/sql-aggregate-function-exercise-{}.php', range(1, 26)],
                         'Formatting query output': ['https://www.w3resource.com/sql-exercises/sql-formatting-output-exercise-{}.php', range(1, 11)],
                         'SQL JOINS': ['https://www.w3resource.com/sql-exercises/sql-joins-exercise-{}.php', range(1, 30)]
                        }
    w3_sql_topics = list(w3_sql_topic_urls.keys())
    
    with open('sql_prompt.txt') as f:
        PROMPT = f.read()
    
    def __init__(self, topic, new_user = True):
        '''
        constructor for SQL session. initializes question tracker to avoid
        repeat questions

        Args:
            topic (str): user's choice for SQL topic to practice
        '''
        self.current_topic = tuple(SQLSession.w3_sql_topic_urls.keys()).index(topic)
        # ensure repeat questions aren't shown for duration of session
        self.question_tracker = {topic:set() for topic in SQLSession.w3_sql_topics}
        self.total_questions_completed = 0
        self.current_topic = 0
        self.current_q_num = 0
        self.is_new_user = new_user
    
    def get_sql_exercise(self, topic):
        '''
        uses methods below to get SQL exercise info
        Args:
            topic (str): user's choice for SQL topic to practice
        Returns:
            dict: parsed results including:
                prompt:exercise question
                solution:provided example solution
                tables:{table name:table in html string}
        '''
        self.is_new_user = False
        exercise_url = self.get_sql_exercise_url(topic)
        results = self.get_sql_exercise_info(exercise_url)
        return results
    
    def get_sql_exercise_url(self, topic):
        '''
        randomly choose a exercise number and return url for randomly
        selected SQL exercise
        Args:
            topic (str): user's choice for SQL topic to practice

        Returns:
            str: w3resource url for selected SQL topic and randomly chosen exercise
        '''
        url, q_nums = SQLSession.w3_sql_topic_urls[topic]
        completed = self.question_tracker[topic]
        q_nums_not_done = set(q_nums) - completed
        if len(q_nums_not_done) == 0:
            q_nums_not_done = q_nums
        random_choice = np.random.choice(list(q_nums_not_done))
        self.current_q_num = random_choice
        self.question_tracker[topic].add(random_choice)
        return url.format(random_choice)

    def get_sql_exercise_info(self, exercise_url):
        '''
        web scrape the SQL exercise info from w3resource, parse the html,
        and format the output

        Args:
            exercise_url (str): w3resource url for selected SQL topic and randomly chosen exercise

        Returns:
            dict: parsed results including:
                prompt:exercise question
                solution:provided example solution
                tables:{table name:table in html string}
        '''
        req_response = requests.get(exercise_url, timeout=5)
        html_content = BeautifulSoup(req_response.content, "html.parser")
        paragraphs = html_content.find_all('p')
        # paragraphs = [date, question name, actual question, tables...]
        prompt = paragraphs[2].text
        solution = html_content.find_all('code')[0].text
        num_tables = 0
        table_strs = {}
        tables = html_content.find_all("pre", attrs={"class": None})
        for table in tables:
            table_name = paragraphs[3+num_tables].text.split(': ')[-1].strip()
            # table_str = table.text
            table_strs[table_name] = str(table)
            num_tables += 1
        results = {'prompt':prompt, 'solution':solution, 'tables':table_strs}
        return results
 
    def openai_api_call(self, openai_api_key, user_input, results):
        '''
        web scrape the SQL exercise info from w3resource, parse the html,
        and format the output

        Args:
            openai_api_key (str): user's OpenAI API key
            user_input (str): user's SQL query
            results (dict): formatted output from w3resource with exercise prompt,
                            example solution, and tables

        Returns:
            Completion: OpenAI Completion object with model output
        '''
        openai.api_key = openai_api_key
        sol = results['solution']
        prompt = f'Solution SQL Query:\n{sol}\nInput SQL Query:{user_input}\nAnswer:\n'
        messages = [{"role": "developer", "content": SQLSession.PROMPT}, 
                    {"role": "user", "content": prompt}]
        completion = openai.chat.completions.create(model="gpt-5-nano-2025-08-07", 
                                                    messages=messages)
        self.total_questions_completed += 1
        return completion
        