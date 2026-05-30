/** @odoo-module **/

import { toRaw } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";
import { session } from "@web/session";

const deleteAction = messageActionsRegistry.get("delete");
const originalCondition = deleteAction.condition;

deleteAction.name = _t("Delete (Admin Only)")

deleteAction.condition = (params) => {
    if (!session.is_built_in_admin) {
        return false;
    }
    return typeof originalCondition === "function"
        ? originalCondition(params)
        : originalCondition;
};

deleteAction.onSelected = ({ message: msg, owner }) => {
    const message = toRaw(msg);
    owner.env.services.action.doAction(
        {
            type: "ir.actions.act_window",
            name: _t("Confirm Message Deletion"),
            res_model: "delete.message.reason.wizard",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_message_id: message.id,
            },
        },
        {
            onClose: async () => {
                const count = await owner.env.services.orm.silent.call(
                    "mail.message",
                    "search_count",
                    [[["id", "=", message.id]]]
                );
                if (!count) {
                    message.delete();
                }
            },
        }
    );
};
