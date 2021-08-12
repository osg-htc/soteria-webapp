/**
 * Set up event listeners and check verifications
 */
function onReady(){
    $("#hub-verification a.check").click(checkHubVerification);
    $("#orc-id-verification a.check").click(checkORCIDLink);
    $("#provision-verification a.check").click(provisionProject);
}

/**
 * Check if user has completed any previous verifications
 */
function checkAll(){
    checkHubVerification();
    checkORCIDLink();
    provisionProject();
}

function checkHubVerification(){
    console.log("Hub Check")

    startVerification("hub-verification");
    getHubVerification();
}

function checkORCIDLink(){
    console.log("ORC ID Check")

    startVerification("orc-id-verification");
    getORCIDVerification();
}

function provisionProject(){
    console.log("Provision Check")

    startVerification("provision-verification");
    getProvisionVerification();
}

/////////////
//  AJAX calls to server check
/////////////

function getHubVerification(){
    $.ajax({
        "url": "/api/v1/verify_harbor_account",
        "success" : reportStatusHub,
        "error" : showErrorHub
    })
}

function getORCIDVerification(){
    $.ajax({
        "url": "/api/v1/verify_orcid",
        "success" : reportStatusORCID,
        "error" : showErrorORCID
    })
}

function getProvisionVerification(){
    $.ajax({
        "url": "/api/v1/create_harbor_project",
        "success" : reportStatusProvision,
        "error" : showErrorProvision
    })
}

/////////////
//  Verification specific wrappers for reportStatus
/////////////

function reportStatusHub(status, textStatus, jqXHR){
    elementId = "hub-verification"

    if(isVerified(status)){
        message = "You currently have an registration at the Hub with username: " + status.data["username"]
    } else {
        message = "To gain the affiliate status, you need to follow the attached link to the Hub" +
            " website and create an registration using the same login as this webpage."
    }

    showMessage(elementId, message)
    endVerification(elementId, isVerified(status))
}

function reportStatusORCID(status, textStatus, jqXHR){
    elementId = "orc-id-verification"

    if(isVerified(status)){
        message = "This registration is currently linked with ORC ID: " + status.data["orc_id"]
    } else {
        message = "To gain the affiliate status, you need to follow the attached link and" +
            " link your ORC ID with your registration"
    }

    showMessage(elementId, message)
    endVerification(elementId, isVerified(status))
}

function reportStatusProvision(status, textStatus, jqXHR){
    let data = status.data
    let elementId = "provision-verification"
    let sub_message = ""
    let message = ""

    if(status.status == 'ok'){
        message = "You have been provisioned a repository! Navigate to the repositories page under 'Account Details' or follow the link " +
            "<a href='" + data['url'] + "'>Repository Page</a> to view your repository."
    } else {
        let error_titles = status.errors.map(error => error.title)
        sub_message = error_titles.join("<br>")
        message = "Click Provision to provision a repository under this registration"
    }

    showMessage(elementId, message)
    showSubMessage(elementId, sub_message, true)
    endVerification(elementId, isVerified(status))
}

/////////////
//  Verification specific wrappers for showMessage related to AJAX error
/////////////

function showErrorHub(jqXHR, textStatus, errorThrown){
    showSubMessage("hub-verification", errorThrown, true)
    endVerification( "hub-verification", false );
}

function showErrorORCID(jqXHR, textStatus, errorThrown){
    showSubMessage("orc-id-verification", errorThrown, true)
    endVerification( "orc-id-verification", false );
}

function showErrorProvision(jqXHR, textStatus, errorThrown){
    showSubMessage("provision-verification", errorThrown, true)
    endVerification( "provision-verification", false );
}

// Util

function isVerified( status ){
    try {
        return status.data.verified;
    }
    catch(err){
        return false
    }
}

// Visual Handlers
function startVerification( element_id ){

    // Start Loading Spinner
    $("#" + element_id + " .status-icon>.failed").attr("hidden", true);
    $("#" + element_id + " .status-icon>.success").attr("hidden", true);
    $("#" + element_id + " .status-icon>.loading").attr("hidden", false);
}

function endVerification( element_id, verified ){
    // End Loading Spinner
    $("#" + element_id + " .status-icon>.loading").attr("hidden", true);
    if( verified ){
        // Add check mark
        $("#" + element_id + " .status-icon>.success").attr("hidden", false);
    } else {
        // Add X indicator
        $("#" + element_id + " .status-icon>.failed").attr("hidden", false);
    }
}

function showMessage( element_id, message ){
    // Add the message
    if( message !== undefined ){
        $("#" + element_id + " .main-message").html(message);
    }
}

function showSubMessage( element_id, message, error=false ){

    // Adjust the color
    if( error ){
        $("#" + element_id + " .sub-message").addClass("error");
    }

    // Add the message
    message = message === undefined ? "" : message;
    $("#" + element_id + " .sub-message").html(message);

}

