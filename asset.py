#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from decimal import Decimal


class Asset(ModelSQL, ModelView):
    """
    Fleet Management Asset
    """
    _name = "fleet.asset"
    _rec_name = 'code'
    _description = "Fleet Management Asset"

    code = fields.Char('Code', required=True, select=1)
    meter_unit =  fields.Many2One("product.uom", "Meter Unit",
        domain=[('category.name', '=', 'Length')])
    status = fields.Selection([
        ('Active', 'Active'),
        ('Out of Service', 'Out of Service'),
        ], "Status", readonly=True, select=1)
    average_fuel_efficiency = fields.Function(
        fields.Numeric("Average Fuel Efficiency", loading="lazy"),
            'get_avg_efficiency')

    # Specifications
    year = fields.Integer("Year")
    make = fields.Char("Make")
    model = fields.Char("Model", select=1)
    serial_number = fields.Char("Serial Number")
    license_plate = fields.Char("Plate Number", select=1)

    # Purchase
    vendor = fields.Many2One("party.party", "Vendor")
    purchase_date = fields.Date("Purchase Date")
    purchase_meter = fields.BigInteger("Purchase Meter")
    warranty_expiration_date = fields.Date("Warranty Expiration Date")
    warranty_expiration_meter = fields.BigInteger("Warranty Expiration Meter")

    # Status
    in_service_date = fields.Date("In Service Date")
    out_of_service_date = fields.Date("Out of Service Date")

    # Comments
    comment = fields.Text('Comment')

    def default_year(self):
        """Get the current year
        """
        date_obj = Pool().get('ir.date')
        return date_obj.today().year

    def get_avg_efficiency(self, ids, name):
        """
        Get average efficiency of the fuel
        """
        purchase_line_obj = Pool().get('purchase.line')
        res = {}
        for asset in self.browse(ids):
            sum_quantity = 0
            purchase_line_ids = purchase_line_obj.search([
                ('asset', '=', asset.id)
                ], order=[('id', 'DESC')], limit=100)
            for purchase_line in purchase_line_obj.browse(purchase_line_ids):
                sum_quantity += Decimal(str(purchase_line.quantity))

            if purchase_line_ids:
                # get the last purchase line for particular asset.
                last_line = purchase_line_obj.browse(
                    purchase_line_ids[-1])
                # get the first purchase line from last 100 records
                # for particular asset.
                first_line = purchase_line_obj.browse(
                    purchase_line_ids[0])
                if len(purchase_line_ids) == 1:
                    avg_efficiency = (first_line.meter_reading - \
                        0)/Decimal(str(purchase_line.quantity))
                else:
                    avg_efficiency = (first_line.meter_reading - \
                        last_line.meter_reading) / (sum_quantity)
            else:
                avg_efficiency = 0
            res[asset.id] = avg_efficiency
        return res

Asset()
