from odoo import _, api, models
from odoo.exceptions import AccessError


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _is_admin(self):
        return self.env.user.id == self.env.ref('base.user_admin').id

    def unlink(self):
        if not self._is_admin():
            raise AccessError(_("Only the Administrator can delete chatter messages."))
        # Standard unlink only notifies message recipients; notify the deleting user too.
        if partner := self.env.user.partner_id:
            partner._bus_send('mail.message/delete', {'message_ids': self.ids})
        return super().unlink()
