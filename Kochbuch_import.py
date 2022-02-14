import my_functions as mf
import pandas as pd

path = r"D:\Benutzer\Angelika\Dokumente\DataScienceProjects\02_Kochbuch\Kochbuch\\"
# First find the files of all recipes
recipe_files = mf.find_recipe_files(f'{path}uebersicht.tex') 

# then extract the ingredients
replace_in_file = {'\\\\':'', '\\textonehalf':'0.5', '\\textonequarter':'0.25', 'Hand voll':'Handvoll'}
units = ['Tasse', 'Tassen', 'ml', 'mL', 'L', 'l', 'g', 'TL', 'EL', 'Dose', 'Prise', 'Stück', 'Spritzer', 'Handvoll']
with open(f'{path}{recipe_files[38]}.tex', encoding='utf-8') as recipe:
    # import latex and replace some annoying things
    recipe_text = recipe.read()
    for annoying, better in replace_in_file.items():
        recipe_text = recipe_text.replace(annoying, better)

    # extract recipe name
    recipe_title = recipe_text[:recipe_text.find('}')].split('{')[-1]
    print(recipe_title)

    # extract ingredients
    ingredients = [['Zutat', 'Teil des Rezepts', 'Menge', 'Einheit',]]
    recipe_ingredients_list = mf.get_ingredients_list(recipe_text)
    ingredient_section = ''
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

        current_ingredient = [ing_name]
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
        # due to spacing issues the unit is sometimes in the 2nd column
        elif '\\,' in ing_amount: # the non-breaking space signifies that the unit is in the first column with the amount
            current_ingredient.append(mf.extract_ingredient_amount(ing_amount.split('\\,')[0])) # amount
            current_ingredient.append(ing_amount.split('\\,')[1].strip(' ')) #unit
        # sometimes the unit is in the 1st column but no non-breaking space was used, here any non-numeric character is recognized as a unit
        elif not ing_amount.isnumeric():
            if ing_amount.split(' ')[0].isnumeric():
                current_ingredient.append(mf.extract_ingredient_amount(ing_amount.split(' ')[0])) #amount
            else:
                current_ingredient.append(1) #unit
                print(f'Check if this has acutally the amount of 1: {ingredient}')
            # sometimes more information ( as in 'kl. Dose') can be found
            ing_unit = []
            for el in ing_amount.split(' '):
                if not el.isnumeric():
                    ing_unit.append(el)
            current_ingredient.append(' '.join(ing_unit)) #unit
        # if the 1st column does not contain a unit, and the 2nd also does not contain a unit
        elif ing_name.split(' ')[0] not in units:
            current_ingredient.append(mf.extract_ingredient_amount(ing_amount)) #amount
            current_ingredient.append('') #unit
        else:
            print('Nicht abgefangen')
            print(ingredient)

        ingredients.append(current_ingredient)
    
    print(pd.DataFrame(ingredients[1:], columns=ingredients[0]))