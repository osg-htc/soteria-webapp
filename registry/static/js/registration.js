/*
 * Event handlers.
 */

let isEnrolled = false;
let linkedOrcid = false;
let linkedHub = false;

function onRegistrationCompletion(){
    if(isEnrolled && linkedHub && linkedOrcid){
        document.getElementById("registration-complete").hidden = false
    }
}


function onReady() {
    $("#enrollment a.check").click(checkEnrollment);
    $("#hub a.check").click(checkHub);
    $("#orcid a.check").click(checkORCID);

    checkAll()

    window.addEventListener("focus", checkAll)
    updateChecks()
}

function updateChecks(){
    let complete = checkAll()
    if(!complete){
        setTimeout(updateChecks, 10000)
    }
}

function checkAll() {
    checkEnrollment();
    checkHub();
    checkORCID();

    return isEnrolled && linkedHub && linkedOrcid
}

function checkEnrollment() {

    // Save a check if it is verified
    if(isEnrolled){
        return true
    }

    startCheck("enrollment");
    $.ajax({
        "url": "/api/v1/users/current/enrollment",
        "success": reportStatusEnrollment,
        "error": reportError.bind(null, "enrollment")
    });
}

function checkHub() {

    // Save a check if it is verified
    if(linkedHub){
        return
    }

    startCheck("hub");
    $.ajax({
        "url": "/api/v1/users/current/harbor_id",
        "success": reportStatusHub,
        "error": reportError.bind(null, "hub")
    });
}

function checkORCID() {

    // Save a check if it is verified
    if(linkedOrcid){
        return
    }

    startCheck("orcid");
    $.ajax({
        "url": "/api/v1/users/current/orcid_id",
        "success": reportStatusORCID,
        "error": reportError.bind(null, "orcid")
    });
}


/*
 * Providing feedback to the user.
 */

function reportStatusEnrollment(status, textStatus, jqXHR) {
    let message;
    let elementId = "enrollment";

    if (isVerified(status)) {
        message = "You have joined SOTERIA using your identity from: " + status.data.idp_name;
    }

    showMainMessage(elementId, message);
    endCheck(elementId, isVerified(status));

    isEnrolled = isVerified(status)
    onRegistrationCompletion()
}

function reportStatusHub(status, textStatus, jqXHR) {
    let message;
    let elementId = "hub";

    if (isVerified(status)) {
        message = "You have a " + status.data.harbor.name + " account with the username: " + status.data.username;
    }

    showMainMessage(elementId, message);
    endCheck(elementId, isVerified(status));

    linkedHub = isVerified(status)
    onRegistrationCompletion()
}

function reportStatusORCID(status, textStatus, jqXHR) {
    let message;
    let elementId = "orcid";

    if (isVerified(status)) {
        message = "Your ORCID iD is: " + status.data.orcid_id;
    }

    showMainMessage(elementId, message);
    endCheck(elementId, isVerified(status));

    linkedOrcid = isVerified(status)
    onRegistrationCompletion()
}

/*
 * Assorted helper functions.
 */

function reportError(elementId, jqXHR, textStatus, errorThrown) {
    showSubMessage(elementId, errorThrown, true);
    endCheck(elementId, false);
}

function isVerified(status) {
    try {
        return status.data.verified;
    }
    catch (err) {
        return false;
    }
}

function startCheck(elementId) {
    $("#" + elementId + " .status-icon>.loading").attr("hidden", false);
    $("#" + elementId + " .status-icon>.success").attr("hidden", true);
    $("#" + elementId + " .status-icon>.failure").attr("hidden", true);
}

function endCheck(elementId, success, hide_failure = false) {
    $("#" + elementId + " .status-icon>.loading").attr("hidden", true);
    if (success) {
        $("#" + elementId + " .status-icon>.success").attr("hidden", false);
        $("#" + elementId + " a.check").hide();
    }
    else {
        $("#" + elementId + " .status-icon>.failure").attr("hidden", hide_failure);
    }
}

function showMainMessage(elementId, message) {
    if (message !== undefined) {
        $("#" + elementId + " .main-message").html(message);
    }
}

function showSubMessage(elementId, message, error = false) {
    if (error) {
        $("#" + elementId + " .sub-message").addClass("error");
    }
    message = message === undefined ? "" : message;
    $("#" + elementId + " .sub-message").html(message);
}

onReady()
