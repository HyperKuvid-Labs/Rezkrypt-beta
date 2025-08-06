# Backend – FastAPI Best Practices

## Recommended Folder Structure

.
├── app
│ ├── init.py
│ ├── main.py
│ ├── dependencies.py
│ ├── routers
│ │ ├── init.py
│ │ ├── items.py
│ │ └── users.py
│ └── internal
│ ├── init.py


---

## Final Project Structure

app/
├── init.py
├── main.py
├── dependencies.py
├── models/
│ ├── init.py
│ ├── candidate.py
│ └── company.py
├── routers/
│ ├── init.py
│ ├── candidate.py
│ └── company.py
├── prisma/
│ ├── init.py
│ ├── schema.py
│ └── prisma_setup.sh
├── internal/
└── init.py

## User Roles

There are two user roles in this setup:

- `candidates`
- `companies`