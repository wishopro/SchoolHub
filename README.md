SchoolHub

Distinctiveness
SchoolHub is a web platform centered around supporting school organizations. Its purpose is to provide a centralized place where teachers can organize and publish assignments such as homework and other tasks, and where students can view all of this information in one location. By separating teacher responsibilities from student access, the platform focuses on academic organization rather than social interaction or commerce.

Complexity
This project is distinct from all previous CS50W projects in both functionality and design. It is not a social network like Project 4, as it does not include following users, social feeds, or post-based interaction. It is also not an e-commerce application like Project 2, since it does not involve product listings, auctions, payments, or transactions. Instead, SchoolHub focuses on organizing and managing school-related information through a centralized platform built specifically for this purpose.
From a backend perspective, the project demonstrates complexity through the use of Django models to represent persistent data stored in a relational database. The application implements user authentication using Django’s built-in authentication system, ensuring that certain features are restricted to logged-in users. Database migrations, model relationships, and admin configuration were required to support the application’s functionality, making the backend more complex than earlier course projects.
On the frontend, the project combines Django templates with JavaScript to create a dynamic and responsive user experience. JavaScript is used to handle client-side behavior and enhance interactivity beyond static page rendering. Static files are managed separately from backend logic, and the layout is designed to be mobile-responsive, requiring additional consideration for usability across different screen sizes.
Overall, the project required integrating backend logic, database design, authentication, frontend templates, JavaScript interactivity, and media handling into a single cohesive system. Designing and connecting these components involved architectural planning and independent problem-solving that goes beyond the scope of the earlier CS50W assignments, demonstrating both originality and technical complexity.



File Structure

- `manage.py` – Django management script
- `schoolhub/` – Project configuration (settings, URLs, WSGI/ASGI)
- `core/` – Main application logic
- `core/models.py` – Database models
- `core/views.py` – Request-handling logic
- `core/urls.py` – URL routing
- `core/templates/` – HTML templates
- `static/` – CSS and JavaScript files
- `media/` – Uploaded media files

How to Run

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   pip install -r requirements.txt
4. Apply migrations:
   python manage.py migrate
5. Run the server:
   python manage.py runserver
6. Open http://127.0.0.1:8000/

Additional Information

This project was developed independently as a final project for CS50W. All code was written specifically for this project and does not reuse code from previous assignments.

Requirements

- Python 3
- Django