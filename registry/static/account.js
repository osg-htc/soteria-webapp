window.onload = function() {
  main();
}

function main() {
    /*
        This attaches the listeners for the clear buttons
     */
    let criteria_select = document.getElementById("criteria")
    criteria_select.addEventListener("change", update_form)
}

function update_form(event){
    console.log(event)
}
