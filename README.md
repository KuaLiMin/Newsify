# SHOPBLOCK 🛍

![alt text](./static/header.png)

[Frontend](https://github.com/KuaLiMin/ShopBlock/tree/main/frontend) | [Backend](https://github.com/KuaLiMin/ShopBlock/tree/main/backend) | [Demo Video](https://www.youtube.com/watch?v=3N9Mm8eZ2Po)

## Table of Contents

1. [What is ShopBlock?](#what-is-shopblock)
   - 1.1 [Demo Video](#demo-video)
2. [Getting Started](#getting-started)
   - 2.1 [Prerequisites](#prerequisites)
   - 2.2 [Setup Instructions](#setup-instructions)
     - [Backend Setup](#backend-setup)
     - [Frontend Setup](#frontend-setup)
   - 2.3 [File Structure](#file-structure)
   - 2.4 [Tech Stack](#tech-stack)
   - 2.5 [Final Report](#final-report)
   - 2.6 [Diagrams](#diagrams)

---

## 1. What is ShopBlock?

ShopBlock is a platform designed not just for buying and selling, but with a focus on supporting sustainable and affordable access to goods and services through rentals. By enabling users to create, post, browse, and manage listings, ShopBlock aims to provide a solution for low-income families who may struggle with the high cost of one-time purchases. The platform also addresses the issue of clutter in the home by offering a space for users to rent out items that are rarely used, like camping gear or specialty tools, allowing others to borrow rather than buy. With features like filtering listings by categories and price, making offers, and completing transactions, ShopBlock provides a flexible, community-oriented marketplace. The inclusion of reviews and ratings also fosters a trustworthy environment where users can confidently connect with one another.

### 1.1 Demo Video

Click on the link below to watch a quick 5-minute demo of the ShopBlock website!  
[Demo Video](https://www.youtube.com/watch?v=3N9Mm8eZ2Po)

---

## 2. Getting Started

This section covers the prerequisites, setup instructions for both frontend and backend, and additional technical details to get ShopBlock up and running.

### 2.1 Prerequisites

Ensure you have the following installed:

- Node.js and npm (for frontend)
- Python 3 and pip (for backend)
- Git for version control

### 2.2 Setup Instructions

This setup guide is divided into frontend and backend sections.

#### Backend Setup

Run these in the `backend` folder.

1. **Create a Virtual Environment**  
   If you don't have a virtual environment already set up, create one and activate it:

   ```bash
   python3 -m venv ./swe-env
   source ./swe-env/bin/activate
   pip3 install -r requirements.txt
   ```

2. **Install the Database**  
   Run migrations to install the database for the first time:

   ```bash
   python3 manage.py migrate
   ```

3. **Apply Database Changes**  
   If you make changes to the models, apply migrations carefully:

   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

4. **Run the Backend Server**  
   Start the server with:

   ```bash
   python3 manage.py runserver
   ```

5. **Testing the Backend**  
   Visit the Swagger UI for API testing at [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/).

6. **Run Unit Tests**

   ```bash
   python manage.py test
   ```

**Developer Notes**

- **models.py**: Contains ORM models corresponding to the database.
- **serializers.py**: Handles input/output formatting for the models.
- **urls.py**: Lists endpoints and maps them to views.
- **views.py**: Contains the main functionality mapped in `urls.py`.

---

#### Frontend Setup

1. **Install Node Modules**  
   In the `/frontend` directory, install the required modules:

   ```bash
   npm install
   ```

2. **Start the Frontend Application**

   ```bash
   npm start
   ```

   The frontend application will run on [http://localhost:3000](http://localhost:3000/).

---

### 2.3 File Structure

Directory structure of ShopBlock. The backend and frontend are to be ran separately.

```
.
├── README.md
├── backend
│   ├── README.md
│   ├── backend
│   ├── db.sqlite3
│   ├── manage.py
│   ├── media
│   ├── mypy.ini
│   ├── requirements.txt
│   └── staticfiles
├── frontend
│   ├── README.md
│   ├── build
│   ├── node_modules
│   ├── package-lock.json
│   ├── package.json
│   ├── public
│   └── src
├── lab1
├── lab2
├── lab3
├── lab4
├── mypy.ini
├── package.json
└── static
    └── header.png
```

### 2.4 Tech Stack

- **Frontend**: React, Material UI
- **Backend**: Django, Django REST Framework
- **Database**: SQLite3
- **APIs**: PayPal for payments, OneMap for location services

### 2.5 Final Report

_Insert SRS link_

### 2.6 Diagrams

_Insert the Diagram_

---
