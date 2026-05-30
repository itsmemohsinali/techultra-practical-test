from lxml import etree

from odoo.tests import new_test_user, tagged, TransactionCase


@tagged('post_install', '-at_install', 'custom_field_service_filter')
class TestAssignedCalendarFilter(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fsm_project = cls.env['project.project'].create({
            'name': 'FSM Calendar Filter Project',
            'is_fsm': True,
            'allow_timesheets': True,
            'company_id': cls.env.company.id,
        })
        cls.user_a = new_test_user(cls.env, login='fsm_assignee_a', groups='industry_fsm.group_fsm_user')
        cls.user_b = new_test_user(cls.env, login='fsm_assignee_b', groups='industry_fsm.group_fsm_user')
        cls.user_c = new_test_user(cls.env, login='fsm_assignee_c', groups='industry_fsm.group_fsm_user')

    @staticmethod
    def _calendar_assignee_domain(inactive_user_ids):
        """Mirror the dynamic calendar filter domain for user_ids."""
        if not inactive_user_ids:
            return []
        return [('user_ids', 'not in', inactive_user_ids)]

    def test_assigned_to_filter_visible_in_calendar_view(self):
        view = self.env.ref('industry_fsm.project_task_view_calendar_fsm')
        arch = etree.fromstring(view.get_combined_arch())
        user_field = arch.xpath("//calendar/field[@name='user_ids']")[0]

        self.assertEqual(user_field.get('filters'), '1')
        self.assertEqual(
            self.env['project.task']._fields['user_ids'].get_description(self.env)['string'],
            'Assigned To',
        )

    def test_filter_single_assignee(self):
        task_a = self.env['project.task'].create({
            'name': 'Task A',
            'project_id': self.fsm_project.id,
            'user_ids': self.user_a,
        })
        task_b = self.env['project.task'].create({
            'name': 'Task B',
            'project_id': self.fsm_project.id,
            'user_ids': self.user_b,
        })
        domain = self._calendar_assignee_domain(self.user_b.ids)
        filtered_tasks = self.env['project.task'].search(domain)

        self.assertIn(task_a, filtered_tasks)
        self.assertNotIn(task_b, filtered_tasks)

    def test_filter_multiple_assignees(self):
        task_a = self.env['project.task'].create({
            'name': 'Task A',
            'project_id': self.fsm_project.id,
            'user_ids': self.user_a,
        })
        task_b = self.env['project.task'].create({
            'name': 'Task B',
            'project_id': self.fsm_project.id,
            'user_ids': self.user_b,
        })
        task_c = self.env['project.task'].create({
            'name': 'Task C',
            'project_id': self.fsm_project.id,
            'user_ids': self.user_c,
        })
        domain = self._calendar_assignee_domain(self.user_c.ids)
        filtered_tasks = self.env['project.task'].search(domain)

        self.assertIn(task_a, filtered_tasks)
        self.assertIn(task_b, filtered_tasks)
        self.assertNotIn(task_c, filtered_tasks)
