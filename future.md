Future Plans: langchain 'RAG framework?'

1. Run attention_loop bases on the array attention.items
    a. this should help reduce neccessary threads

2. include vision analysis.
    a. the ability to tell whats happening in vision using gpt-4 vision
    b. help from screenshots

3. send emails and manage calendar events
    a. using langchain to mass query the apis only once might help with accuracy and simplicty in updating and retreiving specific emails and events. It would also help simplify smooth functions to specifically just system functions.

4. improved user system and context
    a. only use the specified users calendar and email
    b. don't show emails and calendar if user isn't varified
    c. password and username al alternative verification

5. improved UI

6. list ui events

7. add previous converstaion retreival and learning
    a. possibly with langchain.

8. smooth functions update
    a. List of commands with description + langchain? It might remove the need for complex OAI function
    b. only use one function to determin if input is a command, then run langchain command retreival, then run second function to check if the function satisfies the request

9. add session and session management