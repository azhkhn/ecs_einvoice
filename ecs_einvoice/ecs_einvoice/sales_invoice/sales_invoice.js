frappe.ui.form.on("Sales Invoice", "send_to_eta", function(frm) {
    frappe.call({
      method: "ecs_einvoice.ecs_einvoice.sales_invoice.sales_invoice.send_invoice",
      args: {
                'name': frm.doc.name
			},
      callback: function(r) {
          }
    });
    const myTimeout = setTimeout(Reload, 3000);
    function Reload() {
  frm.reload_doc();
}
    //frm.refresh();
    //frm.reload_doc()
  });

 frappe.ui.form.on("Sales Invoice", "get_data_from_eta", function(frm) {
    frappe.call({
      method: "ecs_einvoice.ecs_einvoice.sales_invoice.sales_invoice.get_invoice",
      args: {
                'name': frm.doc.name
			},
      callback: function(r) {
          }
    });
    const myTimeout = setTimeout(Reload, 3000);
    function Reload() {
  frm.reload_doc()
  }
  });

  frappe.ui.form.on("Sales Invoice", "cancel_on_eta", function(frm) {
    frappe.call({
      method: "ecs_einvoice.ecs_einvoice.sales_invoice.sales_invoice.cancel_invoice",
      args: {
                'name': frm.doc.name
			},
      callback: function(r) {
          }
    });
    const myTimeout = setTimeout(Reload, 1000);
    function Reload() {
  frm.reload_doc()
  }
  });

  frappe.ui.form.on("Sales Invoice", "refresh", function(frm){
  if (cur_frm.doc.eta_invoice_link && cur_frm.doc.docstatus == 1) {
    frm.add_custom_button("Print ETA Invoice", function(){
        var myWin = window.open(cur_frm.doc.eta_invoice_link);	});
  }
});

  frappe.ui.form.on("Sales Invoice", "print_invoice", function(frm) {
    frappe.call({
      method: "ecs_einvoice.ecs_einvoice.sales_invoice.sales_invoice.pdf",
      args: {
                'name': frm.doc.name
			},
      callback: function(r) {
          }
    });
   /* const myTimeout = setTimeout(Reload, 1000);
    function Reload() {
  frm.reload_doc()
  }
  */
  });

frappe.ui.form.on("Sales Invoice", "clear_signature", function(frm){
    frappe.db.set_value("Sales Invoice", cur_frm.doc.name, "e_signed", 0);
    frappe.db.set_value("Sales Invoice", cur_frm.doc.name, "signature", "");
    cur_frm.save('Update');
});