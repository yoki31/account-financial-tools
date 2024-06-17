# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    can_transfer = fields.Boolean(
        compute="_compute_can_transfer",
        search="_search_can_transfer",
        help="Allow transfer AUC (running) to Asset",
    )

    def _compute_can_transfer(self):
        for asset in self:
            asset.can_transfer = (
                not asset.method_number
                and asset.value_residual
                and asset.state == "open"
            )

    def _search_can_transfer(self, operator, value):
        if operator == "=":
            return [
                ("method_number", "=", 0),
                ("value_residual", ">", 0),
                ("state", "=", "open"),
            ]
        if operator == "!=":
            return [
                "|",
                "|",
                "|",
                ("method_number", ">", 0),
                ("value_residual", "=", 0),
                ("state", "!=", "open"),
            ]

    def _check_can_transfer(self):
        if not all(self.mapped("can_transfer")):
            raise ValidationError(
                _("Only running assets without depreciation (AUC) can transfer")
            )

    def transfer(self):
        ctx = dict(self.env.context, active_ids=self.ids)
        self._check_can_transfer()
        return {
            "name": _("Transfer AUC to Asset & Create Transfer Journal Entry"),
            "view_mode": "form",
            "res_model": "account.asset.transfer",
            "target": "new",
            "type": "ir.actions.act_window",
            "context": ctx,
        }
