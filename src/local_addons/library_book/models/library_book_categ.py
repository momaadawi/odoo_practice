from odoo import models, fields, api

class BookCategory(models.Model):
    _name = 'library.book.category'

    name = fields.Char(string='Category')
    parent_id = fields.Many2one('library.book.category', string='Parent Category', ondelete='restrict', index = True)
    child_ids = fields.One2many('library.book.category', 'parent_id', string = 'Child Categories')
    # To enable the special hierarchy support, also add the following code
    parent_path = fields.Char(index= True)
    
    _parent_store = True
    _parent_name = 'parent_id'

    # To add a check preventing looping relations, add the following line to the model:
    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_hierarchy():
            raise models.ValidationError('Error! You cannot create recursive categories.')