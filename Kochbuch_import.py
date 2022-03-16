import my_functions as mf
from database_credentials import get_credentials
import pandas as pd
import logging
import sys
import time
import sqlalchemy
# from sqlalchemy.ext.declarative import declarative_base

def main():
    path = r"D:\Benutzer\Angelika\Dokumente\DataScienceProjects\02_Kochbuch\Kochbuch\\"
    # First find the files of all recipes
    recipe_files = mf.find_recipe_files(f'{path}uebersicht.tex') 

    # then import the files
    replace_in_file = {
        '\\textonehalf':'0.5', 
        '\\textonequarter':'0.25', 
        'Hand voll':'Handvoll', 
        '\\textcelsius': '°C', 
        '\\&':'und',
        }
    ingredients = [['RezeptID', 'Zutat', 'RezeptTeil', 'Menge', 'Einheit',]]
    recipes = [['Name', 'StandardMenge', 'Quelle', 'Anweisungen']]
    for recipe_file in recipe_files:
        with open(f'{path}{recipe_file}.tex', encoding='utf-8') as recipe:
            # import latex and replace some annoying things
            recipe_text = recipe.read()
            for annoying, better in replace_in_file.items():
                recipe_text = recipe_text.replace(annoying, better)

            # extract recipe name
            recipe_title = recipe_text[:recipe_text.find('}')].split('{')[-1]
            

            # extract ingredients
            ingredients.extend(mf.extract_ingredients(recipe_text, recipe_title))

            # extract recipe instructions
            instructions_text , standard_portion_size = mf.extract_instructions(recipe_text)

            # find the source 
            source = mf.extract_source(recipe_text)
            recipes.append([recipe_title, standard_portion_size, source, instructions_text])
            logger.info(f'import of {recipe_title} finished')

    # create and format recipes dataframe
    recipes_df = pd.DataFrame(recipes[1:], columns=recipes[0])
    # import tags of recipes (savory/sweet, kind of dish (main, side, cake, sweets), vegetarian/meat)
    recipes_tags = pd.read_csv(r"D:\Benutzer\Angelika\Dokumente\DataScienceProjects\02_Kochbuch\Rezepte_Tags.csv",
                                delimiter=';')
    recipes = pd.merge(recipes_df, recipes_tags[['Name','herzhaft','Gerichtart','Küche','VeggieFleischart']], on ='Name')
    
    # create and format ingredients dataframe
    ingredients = pd.DataFrame(ingredients[1:], columns=ingredients[0])
    ingredients['RezeptID'] = ingredients['RezeptID'].replace(to_replace=dict(zip(recipes.Name,recipes.index)))
    
    # standardize amounts of ingredients to amounts per portion
    ingredients = mf.standardize_amounts(ingredients, recipes)


    
    ### Connect to MariaDB and make tables
    logger.info('Starting connection with MariaDB')
    
    # Credentials to database connection
    hostname, dbname, uname, pwd = get_credentials()

    engine = sqlalchemy.create_engine("mariadb+mariadbconnector://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))

    # Base.metadata.create_all(engine)

    # Convert dataframe to sql table                                   
    recipes.to_sql('recipes', engine, if_exists='fail', index=True, index_label='ID', 
                    dtype = {   'ID':sqlalchemy.Integer(),
                                'Name':sqlalchemy.String(length=75),
                                'StandardMenge':sqlalchemy.Integer,
                                'Quelle':sqlalchemy.String(length=300),
                                'Anweisungen':sqlalchemy.String(length=3500),
                                'herzhaft':sqlalchemy.Boolean(),
                                'Gerichtart':sqlalchemy.String(length=15),
                                'Küche':sqlalchemy.String(length=30),
                                'VeggieFleischart':sqlalchemy.String(length=15),
                    })

    ingredients.to_sql('ingredients', engine, if_exists='fail', index=True, index_label='ID',
                        dtype={     'ID':sqlalchemy.Integer(),
                                    'RezeptID':sqlalchemy.Integer(),
                                    'Zutat':sqlalchemy.String(length=40),
                                    'RezeptTeil':sqlalchemy.String(length=40),
                                    'Menge':sqlalchemy.Float(),
                                    'Einheit':sqlalchemy.String(length=15),
                        })
    logger.info('tables created.')
    return


if __name__ == '__main__':
    ## configuration of logger
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

    file_handler = logging.FileHandler('import.log')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.info(f'start @ {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    logger.info(f'runtime: {round((end-start)/60,1)} m')
