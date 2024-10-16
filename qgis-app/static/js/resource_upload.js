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

// Enable submit button
$("input[type=checkbox]").on("click", function(){
    $("input[type=checkbox]").is(":checked") ? enableSubmit() : disableSubmit()
})