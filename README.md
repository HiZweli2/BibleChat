# BibleChat
#### Video Demo:  https://www.loom.com/share/9735ba4f842448b69728868259d46534
#### Description:
BibleChat is an online chat platform built using Flask that enables users to register as a pastor or under a pastor, allowing for communication between registered users. The platform stores user information in a MySQL database hosted on AWS. After registration, users are directed to a login screen where they must input their username and password to access the platform. Once logged in, users can send messages to anyone registered on the platform and have the option to attach a Bible scripture to their messages.

Components
1. Database
All user information is securely stored in a MySQL database hosted on AWS. The RDS CA certificate file (rds-ca-2019-root.pem) within the static folder enables the API to securely connect to the MySQL database.

2. Application Structure
app.py: Contains the Python API code.
requirements.txt: Lists all the required imports for the app to function, ensuring necessary packages are installed.
static folder: Contains JavaScript code to dynamically alter the user interface based on interactions, a CSS file to style the pages, and an images folder for graphical assets.
Features
Registration: Users can sign up as pastors or under a pastor.
Login: Access to the chat platform requires a username and password.
Messaging: Once logged in, users can send messages to any registered user on the platform.
Scripture Attachment: Users can attach a Bible scripture to their messages, enhancing the spiritual interaction on the platform.
Usage
To run the BibleChat application:

Install the required dependencies listed in requirements.txt.
Ensure the MySQL RDS CA certificate (rds-ca-2019-root.pem) is correctly placed in the static folder.
Run app.py.

- /template: Contains HTML pages for the app.
- /static:
  - /js: JavaScript code for dynamic interface interactions.
  - /css: Stylesheet for the app pages.
  - /images: Image assets for the platform.
  - rds-ca-2019-root.pem: MySQL RDS CA certificate file.

## Setup and Installation

1. Clone the repository: `git clone https://github.com/your-username/BibleChat.git`

2. Install dependencies: `pip install -r requirements.txt`

3. Run the Flask app: `python app.py`

4. Access the application in your web browser at `http://localhost:5000`

## Features and Functionality

- **User Registration**: Users can register as either a pastor or a member under a pastor. During registration, a confirmation code is sent to the user's email address for verification.

- **Email Confirmation**: After registration, users receive a confirmation code via email, ensuring a secure and verified registration process.

- **MySQL Database**: User information is securely stored in a MySQL database hosted on AWS.

- **Login System**: Access to the platform is granted only after successful email confirmation. Users log in using their credentials.

- **Chat Messaging**: Users can send messages to anyone registered on the platform.

- **Scripture Attachment**: A unique feature allows users to attach Bible scriptures to their messages, enhancing the spiritual dimension of conversations.

- **Real-time Updates**: Messages are updated in real-time, and a reload button at the bottom right of the chat screen allows users to fetch new messages.

## Usage

1. Register as a pastor or member.
2. Confirm your email address using the sent confirmation code.
3. Log in with your credentials.
4. Start chatting with others, attaching Bible scriptures to your messages.
5. Use the reload button for real-time updates of new messages.

Note
Ensure that the AWS MySQL credentials are appropriately configured in the app.py to establish a secure connection with the database.

