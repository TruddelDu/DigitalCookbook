import my_functions as mf
import pandas as pd
import logging
import sys
import time


def main():
    path = r"D:\Benutzer\Angelika\Dokumente\DataScienceProjects\02_Kochbuch\Kochbuch\\"
    # First find the files of all recipes
    recipe_files = mf.find_recipe_files(f'{path}uebersicht.tex') 

    # then extract the ingredients
    replace_in_file = {'\\\\':'', '\\textonehalf':'0.5', '\\textonequarter':'0.25', 'Hand voll':'Handvoll'}
    ingredients = [['Rezept', 'Zutat', 'Teil des Rezepts', 'Menge', 'Einheit',]]
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

            logger.info(f'import of {recipe_title} finished')

    print(pd.DataFrame(ingredients[1:], columns=ingredients[0]))


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
