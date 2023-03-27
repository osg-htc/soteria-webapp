/**
 * Contains user related functions
 */

async function getUser(){
    let response = await fetch(`/api/v1/users/current`)
    let json = response.json()
    return json['data']
}

export async function isAffiliate(){
    let user = await getUser()
    return user['is_soteria_affiliate']
}

export async function isMember(){
    let user = await getUser()
    return user['is_soteria_member']
}

export async function isResearcher(){
    let user = await getUser()
    return user['is_soteria_researcher']
}