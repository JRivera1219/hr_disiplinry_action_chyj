# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class HrtypeExpdisiplinary(models.Model):

  _name = 'hr.type.exp.disiplinary'
  _description = 'Modelo para el registro los  tipos de expedientes:'

  name = fields.Char('Tipo Expediente', required = True)
  resumen = fields.Char('Resumen')
  active = fields.Boolean('Active', default=True, store=True, readonly=False)
  image = fields.Binary(string='Image')


