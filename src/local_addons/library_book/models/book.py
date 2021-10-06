# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta

class BookArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default = True)

    def do_archive(self): 
        for record in self: 
            record.active = not record.active 

class Book(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _inherit = ['base.archive']

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

    age_days = fields.Float(
        string = 'Days Since Release',
        compute = '_compute_age',
        inverse = '_inverse_age',
        search = '_search_age',
        store = False,
        compute_sudo = True
    )
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            date = today - timedelta(days = book.age_days)
            book.date_release = date

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days = value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map ={
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]


    author_ids = fields.Many2many('res.partner', string='Auhtors', ondelete='cascade')
    publisher_id = fields.Many2one('res.partner', string = 'publisher', ondelete='set null')

    category_id = fields.Many2one('library.book.category')

    publisher_city = fields.Char(string = "Publisher City", related = 'publisher_id.city', readonly = True)

    ref_doc_id = fields.Reference(selection = '_referencable_models', string = 'Reference Document')
    def name_get(self):
        result = []
        for rec in self:
            rec_name = f'{rec.short_name}, {rec.date_release}'
            result.append((rec.id, rec_name))
        return result

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if not record.date_release: 
                raise models.ValidationError('you have to add release date')

            if record.date_release > fields.Date.today(): 
                raise models.ValidationError('date must be in the past')
            

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')
        ])
        return [(x.model, x.name)for x in models]


class ResPartner(models.Model):
    """
    - authored_book_ids (table) built using the name of the two related models, alphabetically sorted, plus  a _rel suffix. However, we can override this using the relation attribute
    
    - A case to keep in mind is when the two table names are large enough for the automatically 
        generated database identifiers to exceed the PostgreSQL limit of 63 characters. As a rule 
        of thumb, if the names of the two related tables exceed 23 characters, you should use the 
        relation attribute to set a shorter name. 
    """

    _inherit = 'res.partner'
    _order = 'name' #name of partner

    published_book_ids  = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids  = fields.Many2many('library.book', string = 'Authored Book', relation = 'library_book_res_partner_rel')
    count_books = fields.Integer(string = 'Number of Authored Books', compute = '_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for rec in self:
            rec.count_books = len(rec.authored_book_ids)

