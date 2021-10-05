# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Book(models.Model):
    _name = 'library.book'
    _rec_name = 'short_name'
    _description = 'Library Book'
    _order = 'date_release desc, name'

    name = fields.Char('Title', required = True)
    short_name = fields.Char('Short Name', required = True, translate= True, index=True)
    date_release = fields.Date(string="Release Date")
    notes = fields.Text('Internal Notes')
    state = fields.Selection([
        ('draft', 'Not Available'),
        ('available', 'Available'),
        ('lost', 'Lost')
    ], 'state',  default = 'draft')
    description = fields.Html('Description', sanitize= True, strip_style= False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of print?')
    date_updated  = fields.Datetime('Last Update')
    pages = fields.Integer('Number of pages', groups='base.group_user', states = {'lost': [('readonly', True)]}, help='page count', company_dependent = False)
    reader_rating = fields.Float('Reader Average Rating', digits = (14,4))

    book_cost = fields.Float('Book Cost', digits = 'Product Price')

    currency_id = fields.Many2one('res.currency', string = 'Currency')
    retail_price = fields.Monetary('Retail Price', currency_field = 'currency_id')

    author_ids = fields.Many2many('res.partner', string='Auhtors', ondelete='cascade')
    publisher_id = fields.Many2one('res.partner', string = 'publisher', ondelete='set null')

    def name_get(self):
        result = []
        for rec in self:
            rec_name = f'{rec.short_name}, {rec.date_release}'
            result.append((rec.id, rec_name))
        return result


class ResPartner(models.Model):
    """
    - authored_book_ids (table) built using the name of the two related models, alphabetically sorted, plus  a _rel suffix. However, we can override this using the relation attribute
    
    - A case to keep in mind is when the two table names are large enough for the automatically 
        generated database identifiers to exceed the PostgreSQL limit of 63 characters. As a rule 
        of thumb, if the names of the two related tables exceed 23 characters, you should use the 
        relation attribute to set a shorter name. 
    """

    _inherit = 'res.partner'

    published_book_ids  = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids  = fields.Many2many('library.book', string = 'Authored Book', relation = 'library_book_res_partner_rel')