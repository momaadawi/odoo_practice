from odoo import api, fields, models


class LibraryMember(models.Model):
    """
        # There is a shortcut for this inheritance delegation. Instead of creating an _inherits 
        # dictionary, you can use the delegate=True attribute in the Many2one field definition. 
        # This will work exactly like the _inherits option
    """
    _name = 'library.member'
    _inherits  = {'res.partner': 'partner_id'}
    _description = 'New Description'

    partner_id = fields.Many2one('res.partner', ondelete= 'cascade')
    # partner_id = fields.Many2one('res.partner', ondelete= 'cascade', delegate = True)
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date') 
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
