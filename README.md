# N.O.V.A - Neural-Network Opperated Voice Assistant
## Overview
NOVA is a sophisticated, personal AI assistant designed for a wide range of interactive tasks, including voice recognition, face detection, text processing, and event handling. Built with a modular architecture, NOVA integrates seamlessly with OpenAI's services, providing a versatile and dynamic response system. 
She is Designed to be a true Voice-to-voice Assistant. 

## Features
* Voice Interaction: Listen and respond to voice commands using the voice module.
* Facial Recognition: Detect and react to faces using the face module.
* Text Processing: Process and interpret text inputs with process_string.
* Event Handling: Manage and respond to various events using the events module.
* Calendar Integration: Schedule and manage events with calendar.
* OpenAI Integration: Leverage OpenAI's capabilities through open_ai.
* User Management: Handle different users and roles with users.
* Customizable Responses: Modify and force responses using force_response.
* SQLite Database: Store and manage messages in a local SQLite database.
## Installation
* Ensure you have Python 3.x installed on your system.
* Clone the repository: > git clone [repository_url]
* Install required dependencies: > pip install -r requirements.txt
* Run the nova class to start the assistant.
## Usage
* Starting NOVA:
- Create an instance of the nova class and call the start method.
  - ### Without GUI 
     ```
    nova = nova()
    nova.start()
     ```
  - ### With GUI
    * in your terminal/CMD

    ```
    cd my/file/location
    python f_main.py
    ```
    * then you go to `http://127.0.0.1:5000/`
* Interacting with NOVA:
- Use voice commands or type text inputs for interaction.
- Enable face detection to trigger actions based on facial recognition.
* Customizing Responses:
- Modify the responce_promps.json to add new responces.
### UI
  * Map
    ![Screenshot of NOVAs UI MAP](/read_me_images/novaUI-labels.jpg "NOVA Screenshot")
    - Options: This area gives you various ways to change how to interact with NOVA
      *  `Detect Faces`: Starts NOVAs face recognition
      *  `Show Vision`: Must be toggled after Detect Faces. This will show a window of what NOVA Sees
      *  `Listen for Name`: Starts her listening for NOVA
      *  `smooth functions`: Not fully finished but allows you to use non specific wording for commands
      *  `Talk`: Allows NOVA to Verbally read the responce
      *  `Verify User`: Skips the reverify interval and instantly checks for any recognisable users
      *  `update messages`: Updates the UI with any messages in memory.
      *  `Save Chats`: Saves the current Chat into an SQLite db. (She will only Loads Chats from today)
    - Chat Area: Type the message you want to send to NOVA and press enter
    - ChatGPT UI: A less cluttered and more text based UI
      ![Screenshot of simple UI](/read_me_images/Screenshot_2024-02-03_185440.png "NOVA Screenshot")
    - Events Info(incomplete): The area where new events will show.
    - Code Pannel: Click on this dot to bring up the code pannel. This is where Code extraced from NOVAs messages will be put for easy copy paste
      ![Screenshot of code pannel](/read_me_images/Screenshot_2024-02-03_185642.png "NOVA Screenshot")
    - Command input: In this ugly text box you can run commands in the environment where nova is initialized eg (`nova.listening_For_name = True` or `print(nova.OAI.messages)`)
      ![Screenshot of command input](/read_me_images/Screenshot_2024-02-03_190109.png "NOVA Screenshot")
    - Cool looking thing: A cool looking thing.
## Error Handling
  NOVA uses traceback for detailed error reporting.
  Custom exception handling can be implemented for advanced scenarios.
## Multithreading
  NOVA leverages threading for concurrent operations, enhancing responsiveness.
## Configuration Options 
### Unlisted options
  All unlisted definitions in the class init are used functionaly and change dynamically. they shouldn't be changed without great caution.
### NOVA.py
  * `tick_time`: Adjust the frequency of checks in the main loop.
  * `capture_face`: Sets wether she utalize the face module for farious features.
  * `use_text`: Sets wether she take text based inputs.
  * `talk`: Sets wether she should respond to you Vocally.
  * `offline`: Operate NOVA without an internet connection.
  * `name`: The name to be listened for. > this is not yet dynamic and will only change the name she listens for.
  * `smooth_functions`: Sets the ability to not use "commands" eg ("nova alpha protocol set talk off") so you could instead say "please stop responding to me" or other variations.
    * Currently not fully completed in current version
  *  `button_listen_noise`: sets where NOVA will make a noise when she starts listening
  *  `speak(speak_system_name)`: determines what api or package she should use to respond vocally
    * Options are currently:
       *  `'_google'`: using gTTS which is free but not very human like.
       *  `'_pytts'`: using pyTTS which is free not very good but offline
       *  `'_elleven'`: using eleven labs which offers exretmly human like responses but is not free and requires an internet connection
   *  `use_calender`: allows nova to be updated on your events in your google calander and alert you about them.
     * in dev and it requires a google api account
### face.py:
In order to be recognised by NOVA, you will need to add pictures of your self to the known_user_face file in the root folder and include the name of a user found in the json_data/user.json file.
  * `show_vision`: sets wether NOVA should display ver vision.
  * `draw_face`: sets wether NOVA should draw a square around the face of people in her vision.
  * `draw_eyes`: sets wether NOVA should draw a ovals around the eyes of people in her vision.
  * `reverify`: sets wether NOVA should check to see if a users identity has changed.
  * `reverify_interval`: sets the time interval in seconds when she should reverify. 
  * `verify_then_interval`: determins if she should start the interval only after a user has been varified.
### open_ai_handler.py - current master uses version the openai version of 0.28.0. Branch V1.0.1 will have the latest 1.0 update for openai.
  * `max_responce_tokens`: sets the maximum allowed tokens in open ais responce
  * `model`: what model should open AI use eg(`gpt-3.5-turbo`,`gpt-4`)
## Extensibility
  Easily add new modules or features by extending the nova class.
  Integrate with other APIs or services for enhanced capabilities.
## Note
* This is a high-level overview of NOVA's functionality. For detailed implementation and customization, refer to the source code and comments within each module.
