from odoo import models, fields

class ConfirmationWizard(models.TransientModel):
    _name = "confirmation.wizard"
    _description = "Cancel Confirmation Wizard"

    guarantee_id = fields.Many2one("letter.of.guarantee", string="Letter of Guarantee", required=True)

    def confirm_cancel(self):
        self.ensure_one()
        self.guarantee_id.action_canceled()
        return {"type": "ir.actions.act_window_close"}

