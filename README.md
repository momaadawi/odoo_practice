# odoo-practice
### rup app
>
windows:
    python odoo-bin --config=debian/odoo.conf -d dbname
>
self.context.get(parm)active_id, active_ids, active_model, active_domain

>
Prior to Odoo v14, TransientModel does not require any access 
rules. Anyone can create a record, and they can only access records 
created by themselves. With Odoo v14, access rights are compulsory for 
TransientModel
>