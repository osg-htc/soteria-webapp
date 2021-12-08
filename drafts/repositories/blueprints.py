"""
Blueprints for repositories page that shows all of a users repositories
"""

import json

from flask import Blueprint, make_response, render_template

__all__ = ["repositories_bp"]

repositories_bp = Blueprint(
    "repositories", __name__, template_folder="templates"
)


@repositories_bp.route("/", methods=["GET", "POST"])
def index():
    """
    Returns a page where the current user can manage their registration.
    """
    try:
        with open("../data-templates/TEMPLATE-projects.json") as json_file:
            projects = json.load(json_file)

    except Exception:  # This could be a outdated template
        projects = [
            {
                "provisioner": "User_ID_0",
                "name": "Project_0",
                "created": "2020-07-30 19:43:35",
                "updated": "2021-07-30 19:43:35",
                "description": "This is a container for project 0",
                "size": "Size in GB (int)",
                "privacy": "Public/Private",
                "tags": [
                    {
                        "name": "latest",
                        "OS": "Linux/Windows/MacOS",
                        "pulled": "datetime",
                        "pushed": "datetime",
                        "size": "Size of Tag",
                    },
                    {
                        "name": "Tag_1",
                        "OS": "Linux/Windows/MacOS",
                        "pulled": "datetime",
                        "pushed": "datetime",
                        "size": "Size of Tag",
                    },
                ],
                "users": {
                    "admin": [
                        {
                            "name": "User_ID_0",
                            "ORCID": 11235813,
                            "account_type": "Researcher",
                            "account_status": "Days Left (int)",
                        }
                    ],
                    "read": [
                        {
                            "name": "User_ID_2",
                            "ORCID": 11235813,
                            "account_type": "Affiliate/Member/Researcher",
                            "account_status": "Days Left (int)",
                        },
                        {
                            "name": "User_ID_3",
                            "ORCID": 11235813,
                            "account_type": "Affiliate/Member/Researcher",
                            "account_status": "Days Left (int)",
                        },
                    ],
                    "write": [
                        {
                            "name": "User_ID_4",
                            "ORCID": 11235813,
                            "account_type": "Affiliate/Member/Researcher",
                            "account_status": "Days Left (int)",
                        }
                    ],
                },
                "readme": "<h2>This is how this project is used</h2><p>This project was created so that you could run things inside this container to advance your research</p><h4>How to use this container</h4><p>To use this container all you have to do is run the following code in your repo<pre><code>soteria build this/repo</code></pre></p>",
            },
            {
                "provisioner": "User_ID_0",
                "name": "Project_1",
                "created": "2018-07-30 19:43:35",
                "updated": "2019-01-09 08:13:15",
                "description": "This is a container for project 1",
                "size": "Size in GB (int)",
                "privacy": "Public/Private",
                "tags": [
                    {
                        "name": "latest",
                        "OS": "Linux/Windows/MacOS",
                        "pulled": "datetime",
                        "pushed": "datetime",
                        "size": "Size of Tag",
                    },
                    {
                        "name": "Tag_1",
                        "OS": "Linux/Windows/MacOS",
                        "pulled": "datetime",
                        "pushed": "datetime",
                        "size": "Size of Tag",
                    },
                ],
                "users": {
                    "admin": [
                        {
                            "name": "User_ID_0",
                            "ORCID": 11235813,
                            "account_type": "Researcher",
                            "account_status": "Days Left (int)",
                        }
                    ],
                    "read": [
                        {
                            "name": "User_ID_2",
                            "ORCID": 11235813,
                            "account_type": "Affiliate/Member/Researcher",
                            "account_status": "Days Left (int)",
                        },
                        {
                            "name": "User_ID_3",
                            "ORCID": 11235813,
                            "account_type": "Affiliate/Member/Researcher",
                            "account_status": "Days Left (int)",
                        },
                    ],
                    "write": [
                        {
                            "name": "User_ID_4",
                            "ORCID": 11235813,
                            "account_type": "Affiliate/Member/Researcher",
                            "account_status": "Days Left (int)",
                        }
                    ],
                },
                "readme": "<h2>This is how this project is used</h2><p>This project was created so that you could run things inside this container to advance your research</p><h4>How to use this container</h4><p>To use this container all you have to do is run the following code in your repo<pre><code>soteria build this/repo</code></pre></p>",
            },
        ]

    return make_response(
        render_template("repositories.html", projects=projects)
    )
