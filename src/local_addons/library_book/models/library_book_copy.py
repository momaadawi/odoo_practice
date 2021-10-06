from odoo import models, fields, api

class LibraryBookCopy(models.Model):
    #Prototype Inhertince
    # Prototype inheritance does not work if you use the same model name in the 
    # _inherit and _name attributes. If you do use the same model name in the 
    # _inherit and _name attributes, it will just behave like a normal extension 
    # inheritance.
    _name = 'library.book.copy'
    _inherit = 'library.book'
    _description = "Library Book's Copy"   

    copy_name = fields.Char('copy_name') 

# By using _name with the _inherit class attribute at the same time, you can copy the 
# definition of the model. When you use both attributes in the model, Odoo will copy the 
# model definition of _inherit and create a new model with the _name attribute. 