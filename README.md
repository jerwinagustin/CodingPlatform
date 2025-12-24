# University Management System

Welcome to the University Management System project! This document provides a high-level overview of the application, how to run it, and how it works, designed for both non-technical users and developers.

## 🌟 Introduction

This application is a digital platform designed to streamline university operations. Currently, it focuses on secure user management for two main groups:
- **Professors**: Academic staff who manage courses and students.
- **Students**: Learners who enroll in courses and track their progress.

## 🚀 Key Features

- **Professor Portal**: Secure registration and login specifically for faculty members.
- **Student Portal**: Dedicated sign-up and sign-in area for students.
- **Secure Access**: Your data is protected using modern security standards (JWT Authentication), ensuring that only you can access your account.
- **Modern Interface**: A clean, responsive, and easy-to-use web interface.

## 📖 How to Run the Application

Getting started is easy. We have provided a simple script to launch everything for you.

### Prerequisites
Before running, ensure you have the following installed on your computer:
1.  **Python** (for the backend logic).
2.  **Node.js** (for the visual interface).
3.  **MongoDB** (database to store information).

### Step-by-Step Guide
1.  **Navigate to the Project Folder**: Open this folder on your computer.
2.  **Run the Start Script**:
    - Look for a file named `start-dev.ps1`.
    - Right-click it and select "Run with PowerShell" OR open a terminal in this folder and type `.\start-dev.ps1`.
3.  **Access the App**:
    - The script will launch two windows (one for the backend, one for the frontend).
    - Open your web browser and go to: `http://localhost:5173`

*The application should now be visible on your screen!*

## 🏗️ Architecture Overview (Simplified)

For those curious about how this works under the hood, think of this application like a **Restaurant**:

### 1. The Frontend (What You See) 🍽️
* **Technology:** React (built with Vite)
* **Role:** This is the **Dining Area**. It's the beautiful interface you interact with—buttons, forms, and pages. When you click "Login", you are essentially "ordering" a service.

### 2. The Backend (The Logic) 👨‍🍳
* **Technology:** Django (Python)
* **Role:** This is the **Kitchen**. When you submit a form (order), the request goes here. The backend processes your request, checks if your password is correct, or saves your new account details. It decides what to do and sends the "dish" (data) back to the dining area.

### 3. The Database (The Storage) 📦
* **Technology:** MongoDB
* **Role:** This is the **Pantry**. The kitchen (Backend) retrieves user profiles, grades, and other information from here. It's where all the raw "ingredients" (data) are stored safely and persistently.

### 4. Communication (The Waiter) 🗣️
* **Technology:** REST API
* **Role:** The **Waiter** takes your order from the table (Frontend) to the kitchen (Backend) and brings the food back. In our code, this is done via "API Calls."

## 🔧 Technical Stack Summary

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React + Vite | Fast, modern web interface. |
| **Backend** | Django | Robust Python web framework. |
| **Database** | MongoDB | Flexible NoSQL database for storing data. |
| **Auth** | JWT (JSON Web Tokens) | Secure method for handling user sessions. |

## ❓ Troubleshooting

If you encounter issues:
- **"Site can't be reached"**: Ensure the `start-dev.ps1` script ran successfully and both terminal windows are open.
- **"Login failed"**: Check if the MongoDB service is running on your machine.
- **Data not saving**: Ensure you are using the correct credentials for your local database.

---
*Created for the University Management System Project.*
