import numpy as np
from re import split as resplit
import logging

logger = logging.getLogger(__name__)

def find_recipe_files(path):
    """Returns a list of all file names of receipts contained in the file. 
    Recognizes these file name by an '\input' statement.

    Args:
        path (sting): path to the tex-file containing the overview over all recipes

    Returns:
        list: filenames of the recipes
    """
    recipe_files = list()
    with open(path,'r', encoding='utf-8') as ubersicht:
        for line in ubersicht.readlines():
            if line[:6]=='\\input':
                recipe_files.append(line.split('{')[-1].strip()[:-1])
    return recipe_files

def get_ingredients_list(recipe_text):
    """Returns the ingredients as a list.

    Args:
        recipe_text (sting): latex code of recipe

    Returns:
        list: ingredients in a list
    """
    #find the table and from there the next newline
    ingredients_start = recipe_text.find('begin{tabular}{l') + recipe_text[recipe_text.find('begin{tabular}{l')+1:].find('\n') + 1
    ingredients_end = recipe_text.find('end{tabular}')-1 # find the end of the table
    return recipe_text[ingredients_start:ingredients_end].split('\n')

def is_string_float(potential_float):
    """Returns True if the given string can be formatted into a float. Excepts dots and commas as decimal separators.

    Args:
        potential_float (string): the string that might be a float

    Returns:
        boolean: wether or not potential_float is an acutal float
    """
    potential_float = potential_float.replace(',','.')
    try:
        float(potential_float)
        return True
    except ValueError:
        return False

def extract_ingredient_amount(ing_amount):
    """Returns the amount of an ingredient as a float.

    Args:
        ing_amount (sting):  1st column in Ingredients list

    Returns:
        float: amount of the ingredient
    """
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

def extract_ingredients(recipe_text, recipe_title):
    """Retrives the ingredients and respective amounts from a recipe written in latex. 

    Args:
        recipe_text (float): latex code of recipe
        recipe_title (string): title of the recipe

    Returns:
        list: list of lists, each containing the recipe title, the ingredient, the part of the recipe it belongs to, the amount and the unit
    """
    ingredients = list()
    recipe_ingredients_list = get_ingredients_list(recipe_text)
    ingredient_section = ''
    units = ['Tasse', 'Tassen', 'ml', 'mL', 'L', 'l', 'g', 'TL', 'EL', 'Dose', 'Prise', 'Stück', 'Spritzer', 'Handvoll', 'Würfel', 'Bund', 'Zweig', 'Packung']
    for ingredient in recipe_ingredients_list:
        ingredient = ingredient.strip('\t')
        # sometimes the ingredients are not given for the enitre recipe but for sections
        if 'multicolumn' in ingredient:
            ingredient_section = ingredient.strip('}:\\')[ingredient.rfind('{'):]
            continue

        ing_name = ingredient.split('&')[-1]
        ing_amount = ingredient.split('&')[0]

        #clean-up of ingredient name
        if 'textsuperscript' in ing_name:
            ing_name = ing_name[:ing_name.find('\\textsuperscript')]

        current_ingredient = [recipe_title, ing_name]
        current_ingredient.append(ingredient_section)
        
        #do not add empty rows to the database
        if ing_name=='':
            continue
        # the ingredient name can extend to the next row, at least sometimes signified by starting with 'oder '
        elif ing_name[:5]=='oder ':
            ingredients[-1][0] = f'{ingredients[-1][0]} {ing_name}' # this 2nd part of the ingredient name is added to the correct place
            continue
        # some recipes do not have any amount and are given in just one column
        elif ing_amount==ing_name:
            current_ingredient.append(float('NaN')) # amount
            current_ingredient.append('') # unit
        # some ingredients are not given with an amount
        elif ing_amount=='' or ing_amount==' ':
            current_ingredient.append(float('NaN')) #amount
            current_ingredient.append('') #unit
        # some ingredients are not listed with a specific amount
        elif any(relative_amount in ing_amount for relative_amount in ['etwas', 'wenig', 'n.B.']):
            current_ingredient.append(float('NaN')) #amount
            current_ingredient.append('') #unit
        # due to spacing issues the unit is sometimes in the 2nd column
        elif '\\,' in ing_amount: # the non-breaking space signifies that the unit is in the first column with the amount
            current_ingredient.append(extract_ingredient_amount(ing_amount.split('\\,')[0])) # amount
            current_ingredient.append(ing_amount.split('\\,')[1].strip(' ')) #unit
        # sometimes the unit is in the 1st column but no non-breaking space was used, here any non-numeric character is recognized as a unit
        elif not is_string_float(ing_amount):
            if is_string_float(ing_amount.split(' ')[0]):
                current_ingredient.append(extract_ingredient_amount(ing_amount.split(' ')[0])) #amount
                unit_included = True
            elif  any(bindestrich in ing_amount for bindestrich in ['-', '–']):
                current_ingredient.append(extract_ingredient_amount(ing_amount)) #amount
                unit_included = False
            else:
                current_ingredient.append(1) #amount
                logger.info(f'Check if this actually has the amount of 1: {ingredient}')
                unit_included = True
            if unit_included:
                # sometimes more information ( as in 'kl. Dose') can be found
                ing_unit = []
                for el in ing_amount.split(' '):
                    if not el.isnumeric():
                        ing_unit.append(el)
                current_ingredient.append(' '.join(ing_unit)) #unit
            else:
                current_ingredient.append('') #unit - if there is neither a non-breaking space or a normal space then there can't be a unit
        # if the 1st column does not contain a unit, and the 2nd also does not contain a unit
        elif ing_name.split(' ')[0] not in units:
            current_ingredient.append(extract_ingredient_amount(ing_amount)) #amount
            current_ingredient.append('') #unit
        # find units in 2nd columns with the predefined list
        elif ing_name.split(' ')[0] in units:
            current_ingredient.append(extract_ingredient_amount(ing_amount)) #amount
            current_ingredient.append(ing_name.split(' ')[0]) #unit
            current_ingredient[1] == ' '.join(ing_name.split(' ')[1:]) # correct the name of the ingredient
        else:
            logger.warning(f'unable to import the following ingredient row: {ingredient}')
        ingredients.append(current_ingredient)
    return ingredients