from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        result['is_built_in_admin'] = self.env['mail.message']._is_admin()
        return result
