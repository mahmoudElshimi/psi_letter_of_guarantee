from odoo import models, fields

class LogTag(models.Model):
    _name = 'log.tag'
    _description = 'Letter Of Guarantee Tags'

    name = fields.Char('Tag Name', required=True)

