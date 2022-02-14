import numpy as np
from re import split as resplit


def find_recipe_files(path):
    ''' Returns a list of all file names of receipts contained in the file. Recognizes these file name by an '\input' statement.
    path: string, path to the tex-file containing the overview over all recipes
    '''
    recipe_files = list()
    with open(path,'r', encoding='utf-8') as ubersicht:
        for line in ubersicht.readlines():
            if line[:6]=='\\input':
                recipe_files.append(line.split('{')[-1].strip()[:-1])
    return recipe_files

def get_ingredients_list(recipe_text):
    ''' Returns the ingredients as a list.
    recipe_text: string, latex code of recipe
    '''
    #find the table and from there the next newline
    ingredients_start = recipe_text.find('begin{tabular}{l') + recipe_text[recipe_text.find('begin{tabular}{l')+1:].find('\n') + 1
    ingredients_end = recipe_text.find('end{tabular}')-1 # find the end of the table
    return recipe_text[ingredients_start:ingredients_end].split('\n')

def extract_ingredient_amount(ing_amount):
    ''' Returns the amount of an ingredient as a float.
    ing_amount: string, 1st column in Ingredients list
    '''
    # at times a german decimal (,) was used instead of the english (.)
    ing_amount = ing_amount.replace(',','.')
    ing_amount = ing_amount.replace('$\\sim$', '') 

    # sometimes no amount is given
    if ing_amount == '':
        return float('NaN')
    # sometimes the amount is given in fractions
    elif '/' in ing_amount:
        return float(ing_amount.split('/')[0])/float(ing_amount.split('/')[1])
    # sometimes a range is given. in that case reutrn the mean
    elif any(bindestrich in ing_amount for bindestrich in ['-', '–']):
        parts = resplit('-|–', ing_amount.split('\\,')[0])
        return np.mean([float(amount) for amount in parts])
    # elif any(word in ing_amount for word in ['etwas', 'wenig']):
    #     return float('NaN')
    else:
        return float(ing_amount.split('\\,')[0].replace(',','.')) # german decimal point (comma) replaced with dot 
