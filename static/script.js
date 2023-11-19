let bibleNav = document.getElementById("bibleNav");
let sideNav = document.getElementById("mySidenav");
let closeNav = document.getElementById("closeNav");

closeNav.addEventListener("click",()=>{
    sideNav.classList.toggle("displayNav");
});


// Get current user information from server
window.addEventListener("load", () => {
    console.log("now fetching user infor")
    fetch('http://127.0.0.1:5000/currentUserInfor',{
        method: 'GET',
        headers: {
            'Accept': 'application/json'
          }
    }).then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      }).then(data => {
        // Handle the JSON data received from Flask
        console.log(data);
        sessionStorage.setItem("id",data[0])
        sessionStorage.setItem("token",data[3])
      })
      .catch(error => {
        console.error('Fetch Error:', error);
      });
  });



let selectedBook = document.getElementById("selectedBook");
let bookchapter = document.getElementById("bookchapter");
let bookverse = document.getElementById("bookverse");

let firstChapterClick = true;
let previousBook = selectedBook.value;
bookchapter.addEventListener("click",()=>{

    if(firstChapterClick === true && selectedBook.value !== 'book')
    {
        console.log("Getting available chapters based on selected book")
        getChapterAndVerse(selectedBook.value);
        previousBook = selectedBook.value;
        firstChapterClick = false;
    }else if(firstChapterClick === false && selectedBook.value !== previousBook)
    {
        console.log("Deleting provious list of chapters")
        // count the number elemente in bookChapter
        let chaptersCreated = getCount(bookchapter, true);
        // remove all the previously created options/chapters 
        let chapterId = 'a';
        let i = 0;
        while ( i < chaptersCreated - 1) {
            document.getElementById(chapterId).remove();
            chapterId = String.fromCharCode(chapterId.charCodeAt(0) + 1);
            i++;
        }
        console.log("Getting available chapters based on selected book")
        // Then create new options/chapters based on current book
        getChapterAndVerse(selectedBook.value);
        previousBook = selectedBook.value;
    }
});

let firstVerseClick = true;
let previousChapter = bookchapter.value;
let readyToGetScripture = false;
let previousVerse = bookverse.value;
let initialScripture = true;
bookverse.addEventListener("click",()=>{
    let selectedBook = document.getElementById("selectedBook").value;
    let selectedChapter = document.getElementById("bookchapter").value;
    if(firstVerseClick === true && bookchapter.value !== "chapter")
    {
        console.log("Getting initial verses")
        getChapterAndVerse(selectedBook,selectedChapter,bookverse);
        previousChapter = bookchapter.value;
        firstVerseClick = false;
        console.log(bookverse.value)
    }else if (firstVerseClick === false && bookchapter.value !== previousChapter )
    {
        // count the number elemente in bookverse
        console.log("Deleting verses from previous chapter")
        let versesCreated = getCount(bookverse, true);
        // remove all the previously created options/verses 
        for (let i = 0; i < versesCreated - 1; i++) {
            document.getElementById(i.toString()).remove();
        }
        // Then create new options/verses based on current chapter
        console.log("Getting new verses based on current chapter")
        getChapterAndVerse(selectedBook,selectedChapter,bookverse);
        previousChapter = bookchapter.value;
        console.log(bookverse.value)
        initialScripture = true;
    }

    bookverse.value !== 'verse' && bookverse.value !== undefined && bookverse.value !== null? readyToGetScripture = true: readyToGetScripture = false;
    if(readyToGetScripture && initialScripture)
    {
        console.log("Getting initial scripture")
        getScripture(selectedBook,selectedChapter,bookverse.value);
        initialScripture = false;
        previousVerse = bookverse.value;
    }else if(readyToGetScripture && bookverse.value !== previousVerse && document.getElementById("scripture") !== null && document.getElementById("scripture") !== undefined)
    {
        console.log("Deleting current scripture")
        document.getElementById("scripture").remove();
        console.log("Retriving new scripture")
        getScripture(selectedBook,selectedChapter,bookverse.value);
        previousVerse = bookverse.value;
    }
});


/**
 * counts the number of childelements in an html element
 * @param {HTMLElement} parent 
 * @param {boolean} getChildrensChildren 
 * @returns {int} the number of elements in the parent object
 */
function getCount(parent, getChildrensChildren){
    var relevantChildren = 0;
    var children = parent.childNodes.length;
    for(var i=0; i < children; i++){
        if(parent.childNodes[i].nodeType != 3){
            if(getChildrensChildren)
                relevantChildren += getCount(parent.childNodes[i],true);
            relevantChildren++;
        }
    }
    return relevantChildren;
}

/**
 * requests scripture from api based on book , chapter, verse and then displays that scripture in the DOM
 * @param {string} selectedBook 
 * @param {string} selectedChapter 
 * @param {string} bookverse 
 */
function getScripture(selectedBook,selectedChapter,bookverse){
    console.log("Now retriving scripture")
    if(selectedBook !== 'book' && selectedChapter !== 'chapter' && bookverse !== 'verse')
    {
        const currentScripture = document.getElementById("currentScripture");
        const querybody = JSON.stringify({book:selectedBook,chapter:selectedChapter,verse:bookverse});
        fetch('http://127.0.0.1:5000/getScripture',{
            method: "POST",
            body: querybody,
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
            }).then(response => {
                if (!response.ok) {
                throw new Error('Network response was not ok');
                }
                return response.json();
             }).then(scripture =>{
                console.log("creating p tag");
                // Create a new option element
                let p = document.createElement("p");
                //give created element an id
                p.setAttribute("id","scripture");
                p.setAttribute("name","scripture")
                p.setAttribute("class","receivedMessageParagraph");
                // Set the value for the option element
                console.log("Adding scripture text to p tag");
                const node = document.createTextNode(scripture);
                // Add the option element to a select element with the id "mySelect" (replace with your actual select element id)
                p.appendChild(node);
                console.log("Adding p tag to currentScripture div");
                currentScripture.appendChild(p);
            }).catch(error => {
                console.error('Fetch Error:', error);
            })
    }
}

/**
 * requests list of verses or list of chapters from api. Which list it requests is based on the selectedChapter and obj
 * parameters. To get list of chapters call the function with only book param , to get list of verses specify chapter and
 * "bookverse" object 
 * @param {string} book 
 * @param {string} selectedChapter 
 * @param {HTMLElement} obj 
 */
function getChapterAndVerse(book, selectedChapter = "chapter", obj = bookchapter){
    console.log("Loading up verses based on book and chapter")
    if(book === "book")
    {
        alert("Please select a book")
    }
    fetch('http://127.0.0.1:5000/getChapterAndVerse',{
        method: "POST",
        body: JSON.stringify({book:book,chapter:selectedChapter}),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        // Handle the JSON data received from Flask
        let verseId = 0;
        let chapterId = 'a';
        data.forEach(chapterOrVerse => {
            if(chapterOrVerse === "Error quering verse or chapter :(")
            {
                alert("Please check if you`ve selected book , chapter and verse ?")
            }else
            {
                // Create a new option element
                let option = document.createElement("option");
                //give created element an id
                obj === bookverse ? option.setAttribute("id",verseId.toString()):option.setAttribute("id",chapterId);
                // Set the value for the option element
                option.value = chapterOrVerse[0];
                // Set the text content for the option element (visible text)
                option.textContent = chapterOrVerse[0];
                // Add the option element to a select element with the id "mySelect" (replace with your actual select element id)
                obj.appendChild(option);
                obj === bookverse? verseId++: chapterId = String.fromCharCode(chapterId.charCodeAt(0) + 1);
            }
        });
    })
    .catch(error => {
        console.error('Fetch Error:', error);
    });
}


const sendMessagebutton = document.getElementById("sendMessagebutton");
sendMessagebutton.addEventListener("click",()=>{
    const recipient = document.getElementById("recipient").value;
    if(recipient === "users")
    {
        alert("Please select message recipient")
    }
    const typedMessage = document.getElementById("typedMessage").value;
    const chats = document.getElementById("chats");
    let querybody;
    try {
        const word = document.getElementById("scripture").textContent;
        querybody = JSON.stringify({scripture:word,message:typedMessage,recipient:recipient});
      }
      catch(err) {
        console.log("No scripture included sending just the body")
      }
      finally {
        querybody = JSON.stringify({message:typedMessage,recipient:recipient});
      }

    fetch("http://127.0.0.1:5000/",{
        method: "POST",
        body: querybody,
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
        return response.json();
     }).then(response =>{
        if(response === "Message sent")
        {
            alert(response);
            addMyMessageToChats(typedMessage,chats);
        }else
        {
            alert(response);
        }
            
     }).catch(error => {
        console.error('Fetch Error:', error);
     })
})



/**
 * Updates your chats with the latest message you sent
 * @param {string} typedMessage 
 * @param {HTMLElement} chats 
 */
function addMyMessageToChats(typedMessage,chats){
    // Create a new div element
    const div = document.createElement("div");
    //give created element an id
    div.setAttribute("class","sentMessage");
    // Create a new p element
    const p = document.createElement("p");
    //give created element an id
    p.setAttribute("class","receivedMessageParagraph");
    const node = document.createTextNode(typedMessage);
    p.appendChild(node);
    div.appendChild(p);
    chats.appendChild(div);
}


