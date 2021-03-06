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
context : {
        You can also set a context on relational fields, which influences how the field is loaded. 
    By setting the form_view_ref or tree_view_ref keys to the full XML ID of a view, 
    you can select a specific view for this field. This is necessary when you have multiple views 
    of the same type for the same object. Without this key, you get the view with the lowest 
    sequence number, which might not always be desirable.
*   the context is also used to set a default search filter. You can learn more about the 
default search filter in the Defining search views recipe of this chapter 
}
#### notes:
**Important information**
People often forget that they are writing XML files when it comes to domains. 
You need to escape the less-than operator. Searching for records that have 
been created before the current day will have to be written as ```[('create_date', '&lt;', current_date)]```` in XML

* if you only need to check whether such a field is empty, use [[6, False, []]] as your right-hand operand

* you should better define standalone views and use the form_view_ref 
and tree_view_ref keys, as described earlier in the Having an action open a specific 
view recipe of this chapter. rather than embedded views