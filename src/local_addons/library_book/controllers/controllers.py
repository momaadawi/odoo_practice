# -*- coding: utf-8 -*-
# from odoo import http


# class LibraryBook(http.Controller):
#     @http.route('/library_book/library_book/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_book/library_book/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_book.listing', {
#             'root': '/library_book/library_book',
#             'objects': http.request.env['library_book.library_book'].search([]),
#         })

#     @http.route('/library_book/library_book/objects/<model("library_book.library_book"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_book.object', {
#             'object': obj
#         })
