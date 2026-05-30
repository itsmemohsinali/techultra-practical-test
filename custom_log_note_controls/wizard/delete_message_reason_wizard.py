from odoo import fields, models


class DeleteMessageReasonWizard(models.TransientModel):
    _name = 'delete.message.reason.wizard'
    _description = 'Delete Chatter Message'

    reason = fields.Text(string='Deletion Reason', required=True)
    message_id = fields.Many2one('mail.message', required=True, ondelete='cascade')

    def action_confirm_delete(self):
        self.ensure_one()
        message = self.message_id
        # sudo(): audit ACL is read-only; deletion rights are enforced in mail.message.unlink().
        self.env['mail.message.delete.audit'].sudo().create({
            'message_id_char': str(message.id),
            'model': message.model,
            'res_id': message.res_id,
            'message_body': message.body,
            'deleted_by': self.env.user.id,
            'deleted_on': fields.Datetime.now(),
            'delete_reason': self.reason,
        })
        message.unlink()
        return {'type': 'ir.actions.act_window_close'}
