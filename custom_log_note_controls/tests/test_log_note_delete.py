from odoo.exceptions import AccessError
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'log_note_delete_control')
class TestLogNoteDelete(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_employee = cls.env['res.users'].create({
            'name': 'Delete Control Employee',
            'login': 'delete_control_employee',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    def _create_message(self):
        return self.env['mail.message'].create({
            'body': 'Test chatter message',
            'model': 'res.partner',
            'res_id': self.user_admin.partner_id.id,
            'message_type': 'comment',
        })

    def test_regular_user_cannot_delete_message(self):
        message = self._create_message()
        with self.assertRaises(AccessError):
            message.with_user(self.user_employee).unlink()

    def test_admin_delete_via_wizard_creates_audit(self):
        message = self._create_message()
        self.env['delete.message.reason.wizard'].with_user(self.user_admin).create({
            'message_id': message.id,
            'reason': 'Outdated information',
        }).action_confirm_delete()
        audit = self.env['mail.message.delete.audit'].with_user(self.user_admin).search([
            ('message_id_char', '=', str(message.id)),
        ])
        self.assertEqual(len(audit), 1)
        self.assertFalse(message.exists())

    def test_audit_record_stores_required_fields(self):
        message = self._create_message()
        reason = 'Duplicate entry'
        self.env['delete.message.reason.wizard'].with_user(self.user_admin).create({
            'message_id': message.id,
            'reason': reason,
        }).action_confirm_delete()
        audit = self.env['mail.message.delete.audit'].with_user(self.user_admin).search([
            ('message_id_char', '=', str(message.id)),
        ], limit=1)
        self.assertEqual(audit.deleted_by, self.user_admin)
        self.assertTrue(audit.deleted_on)
        self.assertEqual(audit.delete_reason, reason)
