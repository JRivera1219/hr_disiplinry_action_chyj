# -*- coding: utf-8 -*-
# from odoo import http


# class HrDisiplinryActionChyj(http.Controller):
#     @http.route('/hr_disiplinry_action_chyj/hr_disiplinry_action_chyj/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_disiplinry_action_chyj/hr_disiplinry_action_chyj/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_disiplinry_action_chyj.listing', {
#             'root': '/hr_disiplinry_action_chyj/hr_disiplinry_action_chyj',
#             'objects': http.request.env['hr_disiplinry_action_chyj.hr_disiplinry_action_chyj'].search([]),
#         })

#     @http.route('/hr_disiplinry_action_chyj/hr_disiplinry_action_chyj/objects/<model("hr_disiplinry_action_chyj.hr_disiplinry_action_chyj"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_disiplinry_action_chyj.object', {
#             'object': obj
#         })
