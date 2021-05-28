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
    // $().ajax({
    //     "url": "/path",
    //     "method": "GET",
    //     "dataType":"json",
    //     "data": {
    //         "passthrough": "data"
    //     },
    // })
    //     .success(reportStatusHub)
    //     .error(showErrorHub);
}

function getORCIDVerification(){
    // $().ajax({
    //     "url": "/path",
    //     "method": "GET",
    //     "dataType":"json",
    //     "data": {
    //         "passthrough": "data"
    //     },
    // })
    //     .success(reportStatusORCID)
    //     .error(showErrorORCID);
}

function getProvisionVerification(){
    // $().ajax({
    //     "url": "/path",
    //     "method": "GET",
    //     "dataType":"json",
    //     "data": {
    //         "passthrough": "data"
    //     },
    // })
    //     .success(reportStatusProvision)
    //     .error(showErrorProvision);
}

/////////////
//  Verification specific wrappers for reportStatus
/////////////

function reportStatusHub(data, textStatus, jqXHR){
    reportStatus("hub-verification", data)
}

function reportStatusORCID(data, textStatus, jqXHR){
    reportStatus("orc-id-verification", data)
}

function reportStatusProvision(data, textStatus, jqXHR){
    reportStatus("provision-verification", data)
}

/////////////
//  Verification specific wrappers for showMessage related to AJAX error
/////////////

function showErrorHub(jqXHR, textStatus, errorThrown){
    showMessage("hub-verification", textStatus, true)
}

function showErrorORCID(jqXHR, textStatus, errorThrown){
    showMessage("orc-id-verification", textStatus, true)
}

function showErrorProvision(jqXHR, textStatus, errorThrown){
    showMessage("provision-verification", textStatus, true)
}

function isVerified( status ){
    try {
        return provision_status.data.verified;
    }
    catch(err){
        return false
    }
}

// Visual Handlers
function startVerification( element_id ){
    // Start Loading Spinner
    $("#" + element_id + " .status-icon>.loading").attr("hidden", false);
    $("#" + element_id + " .status-icon>.failed").attr("hidden", true);
    $("#" + element_id + " .status-icon>.success").attr("hidden", true);
}

function endVerification( element_id, verified ){
    // End Loading Spinner
    $("#" + element_id + " .status-icon>.loading").attr("hidden", true);;
    if( verified ){
        // Close box and open next one - Add check mark
        $("#" + element_id + " .status-icon>.success").attr("hidden", false);;
    } else {
        // Keep box open and add X indicator
        $("#" + element_id + " .status-icon>.failed").attr("hidden", false);;
    }
}

function showMessage( element_id, message, error=false ){

    // Adjust the color
    if( error ){
        $("#" + element_id + " .message-area").addClass("error-message");
    } else {
        $("#" + element_id + " .message-area").removeClass("error-message");
    }

    // Add the message
    message = message === undefined ? "" : message;
    $("#" + element_id + " .message-area").innerHTML(message);

}

function reportStatus( element_id, status ){

    if( status["error"] ){
        showMessage( element_id, status.error.map(x => x.status + ": " + x.title).join("\n"), true);
        endVerification( element_id, false );
    }

    if( isVerified(status) ){
        showMessage( element_id, status.message );
        endVerification( element_id, true );
    } else {
        showMessage( element_id, "You have not completed the verification process.");
        endVerification( element_id, false );
    }
}
