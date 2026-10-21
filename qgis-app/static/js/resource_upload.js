/**
 * Upload Page
 */

let disableSubmit = () =>{
    $("#licenseAgreed").prop('disabled', true);
    $("#licenseAgreed").removeClass()
    $("#licenseAgreed").addClass("button")
}

let enableSubmit = () => {
    $("#licenseAgreed").prop('disabled', false);
    $("#licenseAgreed").removeClass()
    $("#licenseAgreed").addClass("button is-success")
}

// The submit button stays off until every required checkbox is ticked. This
// covers the licence declarations written into the template and any required
// checkbox the form itself adds, such as the guidelines agreement on maps and
// screenshots.
let requiredCheckboxes = () => $("input[type=checkbox][required]")

let syncSubmit = () => {
    let boxes = requiredCheckboxes()
    if (boxes.length === boxes.filter(":checked").length) {
        enableSubmit()
    } else {
        disableSubmit()
    }
}

syncSubmit()

// Delegated so it also catches checkboxes added to the page after load, and on
// change rather than click so the keyboard works too.
$(document).on("change", "input[type=checkbox][required]", syncSubmit)
