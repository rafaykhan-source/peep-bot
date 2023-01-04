import pandas as pd

def clean_column(col_name: str, df: pd.DataFrame):
    """
    Given a series name of a dataframe and the dataframe.
    Returns cleaned series of string type.

    If the DataFrame does not contain the series, return None.
    If col_name or DataFrame df are None. Return None and prints
    "column name and/or dataframe is of None type."
    """
    if not col_name or not df:
        print("column name and/or dataframe is of None type")
        return None

    if col_name in df.columns:
        names = df[col_name].dropna().drop_duplicates()
        names = pd.Series(names, dtype=pd.StringDtype)
        return names
    else:
        print(f"Spreadsheet column, {col_name}, not found.")
        return None