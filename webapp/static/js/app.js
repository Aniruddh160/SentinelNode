async function indexFolder(){

    let path = document.getElementById("folderPath").value

    let response = await fetch("/index-directory", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ path: path })
    })

    let data = await response.json()

    document.getElementById("answerBox").innerText =
        "Index result: " + JSON.stringify(data)
}


async function askQuestion(){

    let question = document.getElementById("queryInput").value

    let response = await fetch("/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question })
    })

    let data = await response.json()

    document.getElementById("answerBox").innerText = data.answer
}