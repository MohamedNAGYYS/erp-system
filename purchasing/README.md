@"
# Professional ERP System

A complete Enterprise Resource Planning system built with Django.

## Features
- User Management with roles
- Inventory Management (Products, Stock)
- Sales Management (Customers, Orders)
- Purchasing Management (Suppliers, Purchase Orders)
- Automatic stock updates

## Installation
1. Clone repository: \`git clone <url>\`
2. Install requirements: \`pip install -r requirements.txt\`
3. Run migrations: \`python manage.py migrate\`
4. Create superuser: \`python manage.py createsuperuser\`
5. Run server: \`python manage.py runserver\`

## Access
- Admin: http://localhost:8000/admin
- Use superuser credentials

## Project Structure
- accounts/ - Users & authentication
- inventory/ - Products & stock
- sales/ - Customers & sales orders
- purchasing/ - Suppliers & purchase orders
- config/ - Django settings
"@ | Out-File -FilePath README.md -Encoding UTF8