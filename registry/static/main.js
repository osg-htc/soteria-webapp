/**
 * Set up event listeners and check verifications
 */
function onReady(){
    $("#hub-verification a.check").click(checkHubVerification);
    $("#orc-id-verification a.check").click(checkORCIDLink);
    $("#provision-verification a.check").click(provisionProject);
    checkAll();
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
        "url": "/api/v1/verify_orcid_id",
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
    data = status.data
    elementId = "hub-verification"

    if(data.verified == true){
        message = "You currently have an registration at the Hub with username: " + data["username"]
    } else {
        message = "To gain the affiliate status, you need to follow the attached link to the Hub" +
            " website and create an registration using the same login as this webpage."
    }

    showMessage(elementId, message)
    endVerification(elementId, data.verified)
}

function reportStatusORCID(status, textStatus, jqXHR){
    data = status.data
    elementId = "orc-id-verification"

    if(data.verified == true){
        message = "This registration is currently linked with ORCID iD: " + data["orcid_id"]
    } else {
        message = "To gain the affiliate status, you need to follow the attached link and" +
            " link your ORC ID with your registration"
    }

    showMessage(elementId, message)
    endVerification(elementId, data.verified)
}

function reportStatusProvision(status, textStatus, jqXHR){
    data = status.data
    elementId = "provision-verification"

    if(data.verified == true){
        message = "This registration has a repositories already provisioned, go to you " +
            "<a href='/account'>Account Page</a> to view"
    } else {
        message = "Click Provision to provision a repositories under this registration"
    }

    showMessage(elementId, message)
    endVerification(elementId, data.verified)
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

    showMessage(element_id, "")
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
    message = message === undefined ? "" : message;
    $("#" + element_id + " .main-message").html(message);
}


function showSubMessage( element_id, message, error=false ){

    // Adjust the color
    if( error ){
        $("#" + element_id + " .sub-message").addClass("error");
    }

    // Add the message
    message = message === undefined ? "" : message;
    $("#" + element_id + " .sub-message").text(message);

}
