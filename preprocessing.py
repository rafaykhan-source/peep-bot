import pandas as pd
import re

def clean_name(name: str) -> str:
   """Strips name of whitespace and non-alphabetical characters.

   Args:
       name (str): A name.

   Returns:
       str: Cleaned name.
   """
   return re.sub(r"[^a-zA-Z]", '', name).lower()
   

def get_raw_data() -> pd.DataFrame:
   """Obtains raw spreadsheet data.

   Returns:
       pd.DataFrame: raw spreadsheet data.
   """
   raw = pd.read_csv("people.csv", header=1)
   return raw


def get_mentee_data() -> pd.DataFrame:
   """Obtains mentee data.

   Returns:
       pd.DataFrame: Mentee group data.
   """
   raw = get_raw_data()
   people = raw[['Group #', 'Mentor Name', 'Mentee Names']]
   people["Group #"].loc[people["Group #"] == "NEW"] = 37
   people = people.assign(mentees=people["Mentee Names"].str.split(',')).explode('mentees')
   people["group_role"] = "Fall Mentorship Group " + people["Group #"].astype(str)
   people = people.reset_index(drop=True)
   people = people.drop(columns=["Mentee Names"])
   people['clean_name'] = people["mentees"].apply(clean_name)

   return people


def get_mentor_data() -> pd.DataFrame:
   """Obtains mentor data.

   Returns:
       pd.DataFrame: Mentee group data.
   """
   raw = get_raw_data()
   mentors = raw[['Group #', 'Mentor Name']]
   mentors["Group #"].loc[mentors["Group #"] == "NEW"] = 37
   mentors = mentors.rename(columns={'Group #':'group_num', 'Mentor Name':'mentor_name'})
   mentors["group_role"] = "Fall Mentorship Group " + mentors['group_num'].astype(str)
   mentors['clean_name'] = mentors['mentor_name'].apply(clean_name)
   
   return mentors