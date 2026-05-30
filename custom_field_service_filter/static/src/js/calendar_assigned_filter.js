/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { FsmTaskCalendarModel } from "@industry_fsm/views/fsm_task_calendar/fsm_calendar_model";

const ASSIGNEE_FIELD = "user_ids";

function getStorageKey(viewId) {
    return `fsm.calendar.filter.${viewId}.${ASSIGNEE_FIELD}.${user.userId}`;
}

function readStoredStates(viewId) {
    const raw = browser.localStorage.getItem(getStorageKey(viewId));
    if (!raw) {
        return {};
    }
    try {
        return JSON.parse(raw);
    } catch {
        return {};
    }
}

function writeStoredStates(viewId, states) {
    browser.localStorage.setItem(getStorageKey(viewId), JSON.stringify(states));
}

function sectionToStates(section) {
    const states = {};
    for (const filter of section?.filters || []) {
        if (filter.value) {
            states[filter.value] = filter.active;
        }
    }
    return states;
}

function applyStoredState(filter, stored) {
    if (!filter.value) {
        return;
    }
    if (filter.value in stored) {
        filter.active = stored[filter.value];
    } else if (String(filter.value) in stored) {
        filter.active = stored[String(filter.value)];
    }
}

patch(FsmTaskCalendarModel.prototype, {
    makeFilterDynamic(filterInfo, previousFilter, fieldName, rawFilter, rawColors) {
        const filter = super.makeFilterDynamic(...arguments);
        if (fieldName === ASSIGNEE_FIELD) {
            applyStoredState(filter, readStoredStates(this.env.config.viewId));
        }
        return filter;
    },

    async loadDynamicFilterSection(data, fieldName, filterInfo, previousSection) {
        const section = await super.loadDynamicFilterSection(...arguments);
        if (fieldName !== ASSIGNEE_FIELD) {
            return section;
        }

        const viewId = this.env.config.viewId;
        const stored = readStoredStates(viewId);
        const existingIds = new Set(section.filters.map((filter) => filter.value).filter(Boolean));

        for (const filter of section.filters) {
            applyStoredState(filter, stored);
        }

        const missingIds = Object.keys(stored)
            .map((id) => parseInt(id, 10))
            .filter((id) => id && !existingIds.has(id));
        if (missingIds.length) {
            const users = await this.orm.read("res.users", missingIds, ["display_name"], {
                context: { active_test: false },
            });
            for (const assignee of users) {
                section.filters.push({
                    type: "dynamic",
                    recordId: null,
                    value: assignee.id,
                    label: assignee.display_name,
                    active: stored[assignee.id] ?? stored[String(assignee.id)] ?? true,
                    canRemove: false,
                    colorIndex: null,
                    hasAvatar: true,
                });
            }
        }

        writeStoredStates(viewId, { ...stored, ...sectionToStates(section) });
        return section;
    },

    async updateFilters(fieldName, filters, active) {
        if (fieldName === ASSIGNEE_FIELD) {
            const viewId = this.env.config.viewId;
            const stored = readStoredStates(viewId);
            for (const filter of filters) {
                if (filter.value) {
                    stored[filter.value] = active;
                }
            }
            writeStoredStates(viewId, stored);
        }
        await super.updateFilters(...arguments);
    },
});
