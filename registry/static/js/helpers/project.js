/**
 *  Contains project related js functions
 */

export async function getProjects(){
    let response = fetch("/api/v1/users/current/projects")
    let json = response.json()
    return json['data']
}