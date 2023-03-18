# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

class SaleOrder(models.Model):
    _description = 'Aviso de los presupuestos'
    _inherit = 'sale.order'

    presupuestos_value = fields.Integer(compute='_get_length_compute')
    rfc_cliente = fields.Char('RFC Cliente', related='partner_id.vat')
    partner_id = fields.Many2one(
    'res.partner', string='Cliente')


    def _get_length_compute(self):
        presupuestos = self.env['sale.order']
        for record in self:
            record.presupuestos_value = presupuestos.search_count([('user_id', '=', record.user_id.id), ('state', '=', 'draft')])

    def mail_reminder_presupuestos(self):

            match = self.search([('state', '=', 'draft')])
            now = datetime.now()
            date_now = now.date()
            for i in match:
#Se configura un boton con link redireccionador a la vista Sale para mayor comodidad del usuario
                base_url = i.env['ir.config_parameter'].get_param('web.base.url')
                base_url += '/web#action=383&view_type=list&model=%s' %  (i._name)
                aux_date = fields.Date.from_string(i.create_date)
                if aux_date == date_now:
                   if i.user_id:
                        mail_content =  _(

                                     '<br><br> Estimado %s tiene %s presupuestos/cotizaciones por revisar'
                                     '<br> Por favor, ingresar en el siguiente link:'
                                     '<br> <div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                                     'border-color:#875A7B;text-decoration: none; display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; background-image: none; '
                                     'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                                     'Ingresar %s</a></div>') % \
                                   (i.user_id.name,i.presupuestos_value, base_url, i.user_id.name)

                        main_content = {
                                                'subject': _('Revisar los presupuestos del día %s') % (i.create_date),
                                                'author_id': self.env.user.partner_id.id,
                                                'body_html': mail_content,
                                                'email_to': i.user_id.login,
                                            }

                        self.env['mail.mail'].create(main_content).send()
