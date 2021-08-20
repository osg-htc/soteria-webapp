/**
 * Set up event listeners and check verifications
 */
function onReady(){
    $("#hub-verification a.check").click(checkHubVerification);
    $("#orc-id-verification a.check").click(checkORCIDLink);

    checkAll()
}

/**
 * Check if user has completed any previous verifications
 */
function checkAll(){
    checkHubVerification();
    checkORCIDLink();
}

function checkHubVerification(){
    startVerification("hub-verification");
    getHubVerification();
}

function checkORCIDLink(){
    startVerification("orc-id-verification");
    getORCIDVerification();
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

/////////////
//  Verification specific wrappers for reportStatus
/////////////

function reportStatusHub(status, textStatus, jqXHR){
    let message
    let elementId = "hub-verification"

    if(isVerified(status)){
        message = "You currently have an registration at the Hub with username: " + status.data["username"]
    }

    showMessage(elementId, message)
    endVerification(elementId, isVerified(status))
}

function reportStatusORCID(status, textStatus, jqXHR){
    let message
    let elementId = "orc-id-verification"

    if(isVerified(status)){
        message = "This registration is currently linked with ORCID iD: " + status.data["orcid_id"]
    }

    showMessage(elementId, message)
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
        // Remove Button
        $("#" + element_id + " a.check").hide()
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
