# Notes-App

A simple note-taking web application built with [Flask](https://flask.palletsprojects.com/) (Python). This app allows users to register, log in, create, and delete personal notes securely.

## Features

- **User Authentication:** Secure sign-up, login, and logout functionality.
- **Personal Notes:** Each user can create, view, and delete their own notes.
- **Flash Messaging:** User feedback for actions (e.g., errors, successful operations).
- **Responsive UI:** Built with Bootstrap for a clean and responsive interface.

## Project Structure

```
Notes-App/
│
├── website/
│   ├── static/           # Static files (JS, CSS)
│   ├── templates/        # HTML templates
│   ├── __init__.py       # App factory
│   ├── auth.py           # Authentication routes
│   ├── models.py         # Database models
│   ├── views.py          # Main app routes
│
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Setup & Installation

Make sure you have the latest version of Python installed.

```bash
git clone <repo-url>
cd Notes-App
pip install -r requirements.txt
```

## Running The App

Start the Flask development server:

```bash
python main.py
```

## Viewing The App

Open your browser and go to:  
`http://127.0.0.1:5000`

## About the App

### Authorization

The app features a secure authorization portal where you can register with your email and password, and log in again when needed. User sessions are managed securely.

![image](https://github.com/user-attachments/assets/73cfe5f6-c106-4fbb-9e3f-548b150e0c5b)

### Notes Creation and Deletion

Once logged in, you can create new notes and view them in a list. Each note can be deleted individually. All notes are private to each user.

![image](https://github.com/user-attachments/assets/3770f5a7-7b4a-4fab-85b1-9393a73874e2)
![image](https://github.com/user-attachments/assets/c2c7ab60-071a-4b88-84fb-8f2006974ba5)

## Technologies Used

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Bootstrap 4

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

