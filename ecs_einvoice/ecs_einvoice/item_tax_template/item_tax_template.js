frappe.ui.form.on("Item Tax Template", "tax_type", function(frm) {
    cur_frm.set_value('tax_subtype_code', " ");
    cur_frm.set_value('t1_tax_type', "");
    cur_frm.set_value('t2_tax_type', "");
    cur_frm.set_value('t3_tax_type', "");
    cur_frm.set_value('t4_tax_type', "");
    cur_frm.set_value('t5_tax_type', "");
    cur_frm.set_value('t6_tax_type', "");
    cur_frm.set_value('t7_tax_type', "");
    cur_frm.set_value('t8_tax_type', "");
    cur_frm.set_value('t9_tax_type', "");
    cur_frm.set_value('t10_tax_type', "");
    cur_frm.set_value('t11_tax_type', "");
    cur_frm.set_value('t12_tax_type', "");

    if (cur_frm.doc.tax_type == "T1 - Value added tax - ضريبه القيمه المضافه") {
        cur_frm.set_value('tax_code', 'T1');
    }
    if (cur_frm.doc.tax_type == "T2 - Table tax (percentage) - ضريبه الجدول (نسبيه)") {
        cur_frm.set_value('tax_code', 'T2');
    }
    if (cur_frm.doc.tax_type == "T3 - Table tax (Fixed Amount) - ضريبه الجدول (النوعية)") {
        cur_frm.set_value('tax_code', 'T3');
    }
    if (cur_frm.doc.tax_type == "T4 - Withholding tax (WHT) - الخصم تحت حساب الضريبه") {
        cur_frm.set_value('tax_code', 'T4');
    }
    if (cur_frm.doc.tax_type == "T5 - Stamping tax (percentage) - ضريبه الدمغه (نسبيه)") {
        cur_frm.set_value('tax_code', 'T5');
    }
    if (cur_frm.doc.tax_type == "T6 - Stamping Tax (amount) - ضريبه الدمغه (قطعيه بمقدار ثابت)") {
        cur_frm.set_value('tax_code', 'T6');
    }
    if (cur_frm.doc.tax_type == "T7 - Entertainment tax - ضريبة الملاهى") {
        cur_frm.set_value('tax_code', 'T7');
    }
    if (cur_frm.doc.tax_type == "T8 - Resource development fee - رسم تنميه الموارد") {
        cur_frm.set_value('tax_code', 'T8');
    }
    if (cur_frm.doc.tax_type == "T9 - Service charges - رسم خدمة") {
        cur_frm.set_value('tax_code', 'T9');
    }
    if (cur_frm.doc.tax_type == "T10 - Municipality Fees - رسم المحليات") {
        cur_frm.set_value('tax_code', 'T10');
    }
    if (cur_frm.doc.tax_type == "T11 - Medical insurance fee - رسم التامين الصحى") {
        cur_frm.set_value('tax_code', 'T11');
    }
    if (cur_frm.doc.tax_type == "T12 - Other fees - رسوم أخرى") {
        cur_frm.set_value('tax_code', 'T12');
    }
});

frappe.ui.form.on("Item Tax Template", "t1_tax_type", function(frm) {
    if (cur_frm.doc.t1_tax_type == "V001 - Export - تصدير للخارج") {
        cur_frm.set_value('tax_subtype_code', 'V001');
    }
    if (cur_frm.doc.t1_tax_type == "V002 - Export to free areas and other areas - تصدير مناطق حرة وأخرى") {
        cur_frm.set_value('tax_subtype_code', 'V002');
    }
    if (cur_frm.doc.t1_tax_type == "V003 - Exempted good or service - سلعة أو خدمة معفاة") {
        cur_frm.set_value('tax_subtype_code', 'V003');
    }
    if (cur_frm.doc.t1_tax_type == "V004 - A non-taxable good or service - سلعة أو خدمة غير خاضعة للضريبة") {
        cur_frm.set_value('tax_subtype_code', 'V004');
    }
    if (cur_frm.doc.t1_tax_type == "V005 - Exemptions for diplomats, consulates and embassies - إعفاءات دبلوماسين والقنصليات والسفارات") {
        cur_frm.set_value('tax_subtype_code', 'V005');
    }
    if (cur_frm.doc.t1_tax_type == "V006 - Defence and National security Exemptions - إعفاءات الدفاع والأمن القومى") {
        cur_frm.set_value('tax_subtype_code', 'V006');
    }
    if (cur_frm.doc.t1_tax_type == "V007 - Agreements exemptions - إعفاءات اتفاقيات") {
        cur_frm.set_value('tax_subtype_code', 'V007');
    }
    if (cur_frm.doc.t1_tax_type == "V008 - Special Exemptios and other reasons - إعفاءات خاصة و أخرى") {
        cur_frm.set_value('tax_subtype_code', 'V008');
    }
    if (cur_frm.doc.t1_tax_type == "V009 - General Item sales - سلع عامة") {
        cur_frm.set_value('tax_subtype_code', 'V009');
    }
    if (cur_frm.doc.t1_tax_type == "V010 - Other Rates - نسب ضريبة أخرى") {
        cur_frm.set_value('tax_subtype_code', 'V010');
    }
});

frappe.ui.form.on("Item Tax Template", "t2_tax_type", function(frm) {
    if (cur_frm.doc.t2_tax_type == "Tbl01 - Table tax (percentage) - ضريبه الجدول (نسبيه)") {
        cur_frm.set_value('tax_subtype_code', 'Tbl01');
    }
});

frappe.ui.form.on("Item Tax Template", "t3_tax_type", function(frm) {
    if (cur_frm.doc.t3_tax_type == "Tbl02 - Table tax (Fixed Amount) - ضريبه الجدول (النوعية)") {
        cur_frm.set_value('tax_subtype_code', 'Tbl02');
    }
});

frappe.ui.form.on("Item Tax Template", "t4_tax_type", function(frm) {
    if (cur_frm.doc.t4_tax_type == "W001 - Contracting - المقاولات") {
        cur_frm.set_value('tax_subtype_code', 'W001');
    }
    if (cur_frm.doc.t4_tax_type == "W002 - Supplies - التوريدات") {
        cur_frm.set_value('tax_subtype_code', 'W002');
    }
    if (cur_frm.doc.t4_tax_type == "W003 - Purchases - المشتريات") {
        cur_frm.set_value('tax_subtype_code', 'W003');
    }
    if (cur_frm.doc.t4_tax_type == "W004 - Services - الخدمات") {
        cur_frm.set_value('tax_subtype_code', 'W004');
    }
    if (cur_frm.doc.t4_tax_type == "W005 - Sums paid by the cooperative societies for car transportation to their members - المبالغ التي تدفعها الجميعات التعاونية للنقل بالسيارات لاعضائها") {
        cur_frm.set_value('tax_subtype_code', 'W005');
    }
    if (cur_frm.doc.t4_tax_type == "W006 - Commission agency & brokerage - الوكالة بالعمولة والسمسرة") {
        cur_frm.set_value('tax_subtype_code', 'W006');
    }
    if (cur_frm.doc.t4_tax_type == "W007 - Discounts & grants & additional exceptional incentives granted by smoke & cement companies - الخصومات والمنح والحوافز الاستثنائية ةالاضافية التي تمنحها شركات الدخان والاسمنت") {
        cur_frm.set_value('tax_subtype_code', 'W007');
    }
    if (cur_frm.doc.t4_tax_type == "W008 - All discounts & grants & commissions granted by petroleum & telecommunications & other companies - جميع الخصومات والمنح والعمولات التي تمنحها شركات البترول والاتصالات … وغيرها من الشركات المخاطبة بنظام الخصم") {
        cur_frm.set_value('tax_subtype_code', 'W008');
    }
    if (cur_frm.doc.t4_tax_type == "W009 - Supporting export subsidies - مساندة دعم الصادرات التي يمنحها صندوق تنمية الصادرات") {
        cur_frm.set_value('tax_subtype_code', 'W009');
    }
    if (cur_frm.doc.t4_tax_type == "W010 - Professional fees - اتعاب مهنية") {
        cur_frm.set_value('tax_subtype_code', 'W010');
    }
     if (cur_frm.doc.t4_tax_type == "W011 - Commission & brokerage _A_57 - العمولة والسمسرة _م_57") {
        cur_frm.set_value('tax_subtype_code', 'W011');
    }
    if (cur_frm.doc.t4_tax_type == "W012 - Hospitals collecting from doctors - تحصيل المستشفيات من الاطباء") {
        cur_frm.set_value('tax_subtype_code', 'W012');
    }
    if (cur_frm.doc.t4_tax_type == "W013 - Royalties - الاتاوات") {
        cur_frm.set_value('tax_subtype_code', 'W013');
    }
    if (cur_frm.doc.t4_tax_type == "W014 - Customs clearance - تخليص جمركي") {
        cur_frm.set_value('tax_subtype_code', 'W014');
    }
    if (cur_frm.doc.t4_tax_type == "W015 - Exemption - أعفاء") {
        cur_frm.set_value('tax_subtype_code', 'W015');
    }
    if (cur_frm.doc.t4_tax_type == "W016 - Advance payment - دفعات مقدمه") {
        cur_frm.set_value('tax_subtype_code', 'W016');
    }
});

frappe.ui.form.on("Item Tax Template", "t5_tax_type", function(frm) {
    if (cur_frm.doc.t5_tax_type == "ST01 - Stamping tax (percentage) - ضريبه الدمغه (نسبيه)") {
        cur_frm.set_value('tax_subtype_code', 'ST01');
    }
});

frappe.ui.form.on("Item Tax Template", "t6_tax_type", function(frm) {
    if (cur_frm.doc.t6_tax_type == "ST02 - Stamping Tax (amount) - ضريبه الدمغه (قطعيه بمقدار ثابت)") {
        cur_frm.set_value('tax_subtype_code', 'ST02');
    }
});

frappe.ui.form.on("Item Tax Template", "t7_tax_type", function(frm) {
    if (cur_frm.doc.t7_tax_type == "Ent01 - Entertainment tax (rate) - ضريبة الملاهى (نسبة)") {
        cur_frm.set_value('tax_subtype_code', 'Ent01');
    }
    if (cur_frm.doc.t7_tax_type == "Ent02 - Entertainment tax (amount) - ضريبة الملاهى (قطعية)") {
        cur_frm.set_value('tax_subtype_code', 'Ent02');
    }
});

frappe.ui.form.on("Item Tax Template", "t8_tax_type", function(frm) {
    if (cur_frm.doc.t8_tax_type == "RD01 - Resource development fee (rate) - رسم تنميه الموارد (نسبة)") {
        cur_frm.set_value('tax_subtype_code', 'RD01');
    }
    if (cur_frm.doc.t8_tax_type == "RD02 - Resource development fee (amount) - رسم تنميه الموارد (قطعية)") {
        cur_frm.set_value('tax_subtype_code', 'RD02');
    }
});

frappe.ui.form.on("Item Tax Template", "t9_tax_type", function(frm) {
    if (cur_frm.doc.t9_tax_type == "SC01 - Service charges (rate) - رسم خدمة (نسبة)") {
        cur_frm.set_value('tax_subtype_code', 'SC01');
    }
    if (cur_frm.doc.t9_tax_type == "SC02 - Service charges (amount) - رسم خدمة (قطعية)") {
        cur_frm.set_value('tax_subtype_code', 'SC02');
    }
});

frappe.ui.form.on("Item Tax Template", "t10_tax_type", function(frm) {
    if (cur_frm.doc.t10_tax_type == "Mn01 - Municipality Fees (rate) - رسم المحليات (نسبة)") {
        cur_frm.set_value('tax_subtype_code', 'Mn01');
    }
    if (cur_frm.doc.t10_tax_type == "Mn02 - Municipality Fees (amount) - رسم المحليات (قطعية)") {
        cur_frm.set_value('tax_subtype_code', 'Mn02');
    }
});

frappe.ui.form.on("Item Tax Template", "t11_tax_type", function(frm) {
    if (cur_frm.doc.t11_tax_type == "MI01 - Medical insurance fee (rate) - رسم التامين الصحى (نسبة)") {
        cur_frm.set_value('tax_subtype_code', 'MI01');
    }
    if (cur_frm.doc.t11_tax_type == "MI02 - Medical insurance fee (amount) - رسم التامين الصحى (قطعية)") {
        cur_frm.set_value('tax_subtype_code', 'MI02');
    }
});

frappe.ui.form.on("Item Tax Template", "t12_tax_type", function(frm) {
    if (cur_frm.doc.t12_tax_type == "OF01 - Other fees (rate) - رسوم أخرى (نسبة)") {
        cur_frm.set_value('tax_subtype_code', 'OF01');
    }
    if (cur_frm.doc.t12_tax_type == "OF02 - Other fees (amount)	- رسوم أخرى (قطعية)") {
        cur_frm.set_value('tax_subtype_code', 'OF02');
    }
});