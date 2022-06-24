frappe.ui.form.on("Item", "get_item_status", function(frm) {
    frappe.call({
      method: "ecs_einvoice.event_triggers.get_item_status",
      args: {
                'name': frm.doc.name
			},
      callback: function(r) {
          }
    });
    const myTimeout = setTimeout(Reload, 1000);
    function Reload() {
  frm.reload_doc();
}
    //frm.refresh();
    //frm.reload_doc()
  });