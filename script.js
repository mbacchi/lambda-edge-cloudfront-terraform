window.addEventListener("load", getuuid());

function getuuid() {
    var url=window.location.href
    console.log(`url: ${url}`)
    var after_question_mark = url.substring(url.lastIndexOf('?') + 1, url.length);

    console.log(`after_question_mark: ${after_question_mark}`)
    var username = after_question_mark.split('=')[1]

    awaitGitubRequest(username)
}

async function awaitGitubRequest(username) {
    let response = await fetch('https://api.github.com/users/' + username);

    let data = await response.json();

    document.getElementsByClassName("querystring")[0].innerHTML = username
    document.getElementsByClassName("userinfo")[0].innerHTML = JSON.stringify(data, null, "    ")
}
