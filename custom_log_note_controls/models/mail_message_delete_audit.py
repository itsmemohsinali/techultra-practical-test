from odoo import _, fields, models
from odoo.exceptions import AccessError


class MailMessageDeleteAudit(models.Model):
    _name = 'mail.message.delete.audit'
    _description = 'Deleted Chatter Message Audit'
    _order = 'deleted_on desc'

    message_id_char = fields.Char(string='Message ID', required=True, readonly=True)
    model = fields.Char(string='Related Document', readonly=True)
    res_id = fields.Integer(string='Document ID', readonly=True)
    message_body = fields.Html(string='Original Content', readonly=True)
    deleted_by = fields.Many2one('res.users', string='Deleted By', required=True, readonly=True)
    deleted_on = fields.Datetime(string='Deleted On', required=True, readonly=True)
    delete_reason = fields.Text(string='Deletion Reason', required=True, readonly=True)

    def _check_access(self, operation):
        if not self.env['mail.message']._is_admin():
            return self, lambda: AccessError(
                _("Only the Administrator can access deleted message audit records.")
            )
        return super()._check_access(operation)
