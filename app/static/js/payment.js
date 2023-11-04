// Javascript library to provide frontend functions for payment links related functionality.
// It calls our API via Ajax (Needs Jquery)
// Used by our admin dashboard.
// First element of these function is the HTML element who fired this function on click.
// Second element of these function is property ID for which the payment is being processed.

function disable_button(el, text){
    el.disabled = true
    el.style.backgroundColor = "red"
    el.innerText = text
}

function enable_button(el, text){
    el.disabled = false
    el.style = {}
    el.innerText = text
}

class PaymentLinkManager{
    constructor(){
        this.BASE_URL = ""
    }

    async send_payment_link(phone_number, amount, property_id){
        const result = await django.jQuery.ajax({
            type: 'POST',
            url: this.BASE_URL + "/api/payments/send/",
            dataType: "json",
            data: {
                "phone_number": phone_number,
                "amount": amount,
                "property_id": property_id
            },
            headers: {
                'X-CSRFToken': django.jQuery('[name="csrfmiddlewaretoken"]').attr('value')
            },
            async: "false",
        });
        return result
    }

    async resend_payment_link(payment_link_id){
        const result = await django.jQuery.ajax({
            type: 'POST',
            url: `${this.BASE_URL}/api/payments/${payment_link_id}/resend/`,
            headers: {
                'X-CSRFToken': django.jQuery('[name="csrfmiddlewaretoken"]').attr('value')
            },
            headers: {
                'X-CSRFToken': django.jQuery('[name="csrfmiddlewaretoken"]').attr('value')
            },
            async: "false",
        });
        return result
    }

    async cancel_payment_link(payment_link_id){
        const result = django.jQuery.ajax({
            type: 'POST',
            url: `${this.BASE_URL}/api/payments/${payment_link_id}/cancel/`,
            headers: {
                'X-CSRFToken': django.jQuery('[name="csrfmiddlewaretoken"]').attr('value')
            },
            async: "false",
        });
        return result
    }
}

async function send_payment_link(el, property_id){
    let row, phone_number, amount;
    try {
        row = el.parentNode.parentNode.parentNode.parentNode
        phone_number = String(row.querySelector('.field-phone_number input').value || "")
        amount = Number(row.querySelector('.field-amount input').value || 0)

        // Validations
        if (! /^\d{10}$/.test(phone_number)){
            alert("Provide a valid 10 digit number")
            return
        }
        if (amount < 1){
            alert("Provide a valid amount")
            return
        }

        // Call Backend
        disable_button(el, "sending..")
        let plm = new PaymentLinkManager()
        let result = await plm.send_payment_link(phone_number, amount, property_id)
        alert("Payment link sent.")
    }
    catch (err){
        console.error(err)
        alert(err + "contact Backend team.")
        return
    }
    finally {
        enable_button(el, "Send Payment Link")
    }
}

async function resend_payment_link(el, property_id, payment_link_id){
    let row, phone_number, amount;
    try {
        disable_button(el, "resending..")
        let plm = new PaymentLinkManager()
        let result = await plm.resend_payment_link(payment_link_id)
        alert("Payment link resent.")
    }
    catch (err){
        console.error(err)
        alert(err + "contact Backend team.")
        return
    }
    finally {
        enable_button(el, "Resend")
    }
}

async function cancel_payment_link(el, property_id, payment_link_id){
    let row, phone_number, amount;
    try {
        disable_button(el, "cancelling..")
        let plm = new PaymentLinkManager()
        let result = await plm.cancel_payment_link(payment_link_id)
        alert("Payment link cancelled.")
    }
    catch (err){
        console.error(err)
        alert(err + "contact Backend team.")
        return
    }
    finally {
        enable_button(el, "Cancel")
    }
}
