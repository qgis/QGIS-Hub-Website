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

// Disable submit button
disableSubmit()

// Enable submit button if all required checkboxes with id='declaration' are checked
$("input[type=checkbox][required][id='declaration']").on("click", function(){
    let allChecked = $("input[type=checkbox][required][id='declaration']").length === $("input[type=checkbox][required][id='declaration']:checked").length;
    allChecked ? enableSubmit() : disableSubmit();
})