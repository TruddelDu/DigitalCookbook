# DigitalCookbook
Digitalizing a cookbook written in Latex to fill a mySQL database in a first step. This database is planned to be used for a private website or App to have easier access to our most favorite recipes. 

This database is planned to allow functionalities such as: adapting the amounts of ingredients according to portions and finding recipes based on tags (e.g. 'vegetarian', 'quick').

## Entity Relationship Diagram of the database 
![EntityRelationshipDiagram2](https://user-images.githubusercontent.com/68091502/158393961-c7c2ead2-cf4e-43c6-8ed5-b398e2f04fc3.jpg)

For ease of searching recipes or browsing the cookbook with filters, each recipe is tagged with important information. This ranges from the very basic flavour profile (savory/sweet) to the kind of dish (main, side, dessert, cake etc.), more defined flavour profile (mediteranean, mexican etc.) and if the dish contains meat (and which one). 

The ingredient amounts are saved for just one portion, which should simplify the automatic calculation for different portions. However, a standard portion size is attached to every recipe at which it will be displayed by default.

## Technologies
- python  3.9.7 
  - matplotlib 3.5.0
  - numpy 1.21.5
  - pandas 1.3.5
  - sqlalchemy 1.4.27
