import sys
import pandas as pd

from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    Args:
        messages_filepath: Path to disaster_messages dataset.
        categories_filepath: Path to disaster_categories dataset.
    Returns:
        df: Merged dataset
    '''
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = messages.merge(categories, how='inner', on='id')
    return df


def clean_data(df):
    '''
    Args:
        Merged Dataset from load_data function
    Returns:
        Cleaned Dataset
    '''
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True)
    # select the first row of the categories dataframe
    row = categories.iloc[0]

    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = row.apply(lambda x: x[:-2])
    # rename the columns of `categories`
    categories.columns = category_colnames
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x: x[-1])

        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
    df = df.drop(columns=['categories'])
    df[categories.columns] = categories
    # drop duplicates
    df = df.drop_duplicates()
    # Replacing 2 with 0 in related column as the other columns distribution for related=2 is same as related=0
    df['related'].replace(2, 0, inplace=True)
    return df
    


def save_data(df, database_filename):
    '''
    Args:
        cleaned DF, database file name
    '''
    engine = create_engine(f"sqlite:///{database_filename}")
    df.to_sql('processed_df', engine, index=False)  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()