**Send this to anyone who clones your repo.**

**These are the required installations for your Factory AI Attendance System.**



**Backend Packages** 

**-----------------**

**Inside: backend**



Run:



pip install fastapi uvicorn psycopg2-binary python-dotenv

AI Engine Packages



**Inside: ai-engine**

**------------------**

Run:



pip install deepface opencv-python tensorflow tf-keras psycopg2-binary pandas numpy

Frontend Packages



**Inside: frontend\\frontend-app**

**-----------------------------**

Run:



npm install



If node modules missing:



npm install react react-dom react-router-dom axios recharts

Required Software



Install these separately:



Python



Python Downloads



**Recommended:**



Python 3.11

Node.js



**Node.js Recommended:**



Node.js 20+

PostgreSQL



**PostgreSQL Downloads Recommended:**



PostgreSQL 16



**Run Commands :** 

**-------------**



**Backend** 

uvicorn app.main:app --reload --port 8001/8000



**Frontend**

npm run dev



**AI Engine**

python multi\_camera\_system.py



**Database Credentials Example**

host="localhost"

database="factory\_ai"

user="postgres"

password="YOUR\_PASSWORD"

port="5432"



**Important Before running!** 



create PostgreSQL database

create attendance\_logs table

add face images inside dataset folder

install all packages inside virtual environment (venv).

