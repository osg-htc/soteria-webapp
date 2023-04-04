/*
 * Event handlers.
 */

function onReady() {
    $("#enrollment a.check").click(checkEnrollment);
    $("#hub a.check").click(checkHub);
    $("#orcid a.check").click(checkORCID);
    $("#project a.check").click(createProject);  // create the project only when asked

    checkEnrollment();
    checkHub();
    checkORCID();
    checkProject();
}

function checkEnrollment() {
    startCheck("enrollment");
    $.ajax({
        "url": "/api/v1/users/current/enrollment",
        "success": reportStatusEnrollment,
        "error": reportError.bind(null, "enrollment")
    });
}

function checkHub() {
    startCheck("hub");
    $.ajax({
        "url": "/api/v1/users/current/harbor_id",
        "success": reportStatusHub,
        "error": reportError.bind(null, "hub")
    });
}

function checkORCID() {
    startCheck("orcid");
    $.ajax({
        "url": "/api/v1/users/current/orcid_id",
        "success": reportStatusORCID,
        "error": reportError.bind(null, "orcid")
    });
}

function checkProject() {
    startCheck("project");
    $.ajax({
        "url": "/api/v1/users/current/starter_project",
        "success": reportStatusProject,
        "error": reportError.bind(null, "project")
    });
}

function createProject() {
    startCheck("project");
    $.ajax({
        "url": "/api/v1/users/current/starter_project",
        "type": "POST",
        "success": checkProject,
        "error": reportError.bind(null, "project")
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
}

function reportStatusHub(status, textStatus, jqXHR) {
    let message;
    let elementId = "hub";

    if (isVerified(status)) {
        message = "You have a " + status.data.harbor.name + " account with the username: " + status.data.username;
    }

    showMainMessage(elementId, message);
    endCheck(elementId, isVerified(status));
}

function reportStatusORCID(status, textStatus, jqXHR) {
    let message;
    let elementId = "orcid";

    if (isVerified(status)) {
        message = "Your ORCID iD is: " + status.data.orcid_id;
    }

    showMainMessage(elementId, message);
    endCheck(elementId, isVerified(status));
}

function reportStatusProject(status, textStatus, jqXHR) {
    let message;
    let elementId = "project";

    if (isVerified(status)) {
        harbor_name = status.data.harbor.name;
        harbor_projects_url = status.data.harbor.projects_url;
        project_name = status.data.project.name;

        message = "You have a private project on " + harbor_name + " " +
            "with the name <a href='" + harbor_projects_url + "'>" + project_name + "</a>.";
    }

    showMainMessage(elementId, message);
    endCheck(elementId, isVerified(status), true);
}

function reportError(elementId, jqXHR, textStatus, errorThrown) {
    showSubMessage(elementId, errorThrown, true);
    endCheck(elementId, false);
}

/*
 * Assorted helper functions.
 */

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
