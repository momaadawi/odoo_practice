# -*- coding: utf-8 -*-

from ast import parse
import logging
from odoo import models, fields, api
from datetime import timedelta
from enum import Enum
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class BookArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default = True)

    def do_archive(self): 
        for record in self: 
            record.active = not record.active 

class State(Enum):
    draft = 'Not Available'
    available = 'Available'
    borrowed = 'Borrowed'
    lost = 'Lost'

class Book(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _inherit = ['base.archive']

    name = fields.Char('Title', required = True)
    isbn = fields.Char('ISBN')
    old_edition = fields.Many2one(comodel_name='library.book', string='Old Edition')
    manager_remarks = fields.Text('Manager Remarks')
    short_name = fields.Char('Short Name', required = True, translate= True, index=True)
    date_release = fields.Date(string="Release Date")
    notes = fields.Text('Internal Notes')
    state = fields.Selection([
        ('draft', 'Not Available'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
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

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        """
        helper method to check whether a state transition is allowed
        """
        allowed = [('draft', 'available'), 
                   ('available', 'borrowed'), 
                   ('borrowed', 'available'), 
                   ('available', 'lost'), 
                   ('borrowed', 'lost'), 
                   ('lost', 'available')]
        return (old_state, new_state) in allowed
    
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _(f'Moving from {book.state} to {new_state}')
                raise UserError(msg)

    def make_available(self):
        self.change_state(State.available.name)
    def make_borrowed(self):
        self.change_state(State.borrowed.name)
    def make_lost(self):
        self.change_state(State.lost.name)
    
    def log_all_library_members(self): 
        # this is empty set of library member
        library_member_model = self.env['library.member']

        all_members = library_member_model.search([])
        print("ALL MEMBERS: " , all_members)
        return True

    def change_update_date(self):
        """
            checking whether the book recordset that's passed as self contains 
            exactly one record by calling ensure_one(). This method will raise an exception if this 
            is not the case
        """
        
        self.ensure_one()
        self.date_release = fields.Date.today()

    def find_book(self):
        domain = [
            '|',
                '&', ('name', 'ilike', 'Book Name'),
                     ('category_id.name', 'ilike', 'Category Name' ),
                '&', ('name', 'ilike', 'Book Name 2'),
                     ('name', 'ilike', 'category name 2')

        ]

        return self.search(domain)

    def find_partner(self):
        partnerObj = self.env['res.partner']
        domain = [
            '&',
                ('name', 'ilike', 'Mohamed'),
                ('company_id.name', 'ilike', 'odoo')
        ]

        partner = partnerObj.search(domain)
                
    def createRecordset(self):
        partner = self.env['res.partner'].search([])
        bookPartners = self.search([]).author_ids
        result = partner & bookPartners
        print(result)

    @api.model
    def books_with_multiple_authors(self, all_books):
        _logger.debug('creating books with multiple authors')        
        import pdb; pdb.set_trace()
        def predicate(book):
            if len(book.author_ids) > 0:
                return True
            return False
        result = self.filtered(predicate)
        return result
    # OR
    # @api.model
    # def books_with_multiple_authors(self, all_books):
    #     return all_books.filter(lambda b: len(b.author_ids > 1))

    @api.model
    def books_with_categories(self, all_books):
        res = self.filtered(lambda b: b.category_id)
        print(res)
        return res
    @api.model
    def books_sorted_by_name(self, all_books):
        all_books.sorted(key= 'release_date', reverse = True)

    @api.model
    def create(self, values):
        if  not self.user_has_groups('library_book.group_librarian'):
            if 'manager_remarks' in values:
                 raise UserError('you are not allowed to modify', 'manager_remarks')
        return super(Book, self).create(values)

    def write(self, values):
        if  not self.user_has_groups('library_book.group_librarian'):
            if 'manager_remarks' in values:
                 raise UserError('you are not allowed to modify', 'manager_remarks')
        
        return super(Book, self).write(values)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
            args = [] if args is None else args.copy()
            if not(name == '' and operator == 'ilike'):
                args += ['|', '|', '|',
                    ('name', operator, name),
                    ('isbn', operator, name),
                    ('author_ids.name', operator, name)
                 ]
            return super(Book, self)._name_search(
                name=name, args=args, operator=operator,
                limit=limit, name_get_uid=name_get_uid)        

    def grouped_data(self):
       data =  self._get_average_cost()
       _logger.info(f'total price for books in CATEGORY: {data}', )

    @api.model
    def _get_average_cost(self):
      return  self.read_group(
                domain= [('book_cost', '>', 0)],
                fields=['category_id', 'book_cost:sum'],
                groupby=['category_id'], lazy= False, limit= 10)

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
    
