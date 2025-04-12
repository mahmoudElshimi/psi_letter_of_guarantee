import time
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LetterOfGuarantee(models.Model):
    _name = "letter.of.guarantee"
    _description = "Letter Of Guarantee"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Reference", required=True, tracking=True)
    _sql_constraints = [
        ("unique_name", "unique(name)", "The Reference must be unique.")
    ]

    partner_id = fields.Many2one(
        "res.partner", string="Partner", required=True, ondelete="restrict", tracking=True
    )
    journal_id = fields.Many2one(
        "account.journal", string="Journal", required=True, ondelete="restrict", tracking=True
    )
    bank_id = fields.Many2one(
        "res.bank",
        string="Bank",
        related="journal_id.bank_id",
        readonly=True,
        store=True,
        ondelete="restrict",
    )

    amount = fields.Float(string="Amount", required=True, tracking=True)
    issuance_fees = fields.Float(string="Issuance Fess", required=True, tracking=True)
    interest = fields.Float(string="Interest", required=True, tracking=True)

    canceled_by = fields.Many2one(
        "res.users",
        string="Canceled By",
        default= None,
        readonly=True,
    )
    issue_date = fields.Date(string="Issue Date", required=True, tracking=True)
    expiry_date = fields.Date(string="Expiry Date", required=True, tracking=True)
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("canceled", "Canceled")],
        string="State",
        default="active",
        compute="_compute_state",
        store=True,
        readonly=True,
        tracking=True,
    )
    feedback = fields.Selection(
        [
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("under_examination", "Under Examination"),
        ],
        required=True,
        string="Bank Feedback",
        default="under_examination",
        tracking=True, 
    )
    log_type = fields.Selection(
        [("primary", "Primary"), ("final", "Final")],
        required=True,
        string="Type",
        default="primary",
        tracking=True, 
    )
    description = fields.Text(string="Description", tracking=True)
    tag_ids = fields.Many2many("log.tag", string="Tags", tracking=True)
    pdf_file = fields.Binary(string="PDF File", tracking=True)
    bank_account_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        related="journal_id.bank_account_id",
        store=True,
        ondelete="restrict",
    )
    default_account_id = fields.Many2one(
        "account.account",
        string="Default Account",
        related="journal_id.default_account_id",
        store=True,
        ondelete="restrict",
    )

    def copy(self, default=None):
        if default is None:
            default = {}
        # Clear the "name" and "canceled_by" for the duplicate
        default["name"] = int(time.time()) 
        default["canceled_by"] = None
        return super(LetterOfGuarantee, self).copy(default)

    def action_canceled(self):
        for record in self:
            record.write({
                "state": "canceled",
                "canceled_by": self.env.user.id, 
            })
    from odoo.exceptions import ValidationError

    def write(self, vals):
        for record in self:
            if record.state == "canceled":
                raise ValidationError("You cannot modify a canceled Letter of Guarantee.")
        return super(LetterOfGuarantee, self).write(vals)



    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        if self.journal_id:
            # Set the Default Account
            self.default_account_id = self.journal_id.default_account_id
            # Set the Bank Account if needed
            partner_bank = self.env["res.partner.bank"].search(
                [("bank_id", "=", self.journal_id.bank_id.id)], limit=1
            )
            self.bank_account_id = partner_bank
        else:
            self.default_account_id = False
            self.bank_account_id = False

    @api.depends("expiry_date")
    def _compute_state(self):
        for record in self:
            if record.state== "canceled":
                pass
            elif record.expiry_date and record.expiry_date <= fields.Date.today() and record.state != "canceled":
                record.state = "expired"
            else:
                record.state = "active"


    @api.constrains("amount", "issuance_fees", "interest")
    def _check_value(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("The amount must be greater than zero.")
            if record.issuance_fees <= 0:
                raise ValidationError("The fees must be greater than zero.")
            if record.interest <= 0:
                raise ValidationError("The interest must be greater than zero.")

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        for record in self:
            if (
                record.issue_date
                and record.expiry_date
                and record.expiry_date <= record.issue_date
            ):
                raise ValidationError(
                    "The Expiry Date must be later than the Issue Date."
                )
