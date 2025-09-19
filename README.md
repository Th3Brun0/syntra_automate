# syntra_automate

/frontend        → React (Vite)
/backend         → FastAPI (Python)
/scripts         → utilitários (incluindo install_syntra.sh)
/docs            → documentação
/tests           → testes unitários e integração


# Requirements
Ubuntu 20.04, 22.04 ou 24.04
Python 3.11+
Node.js 18+
PostgreSQL 14+
Git

🔒 Security
Password hashing with bcrypt
Encrypted storage of SSH keys
CSRF protection + JWT authentication + input validation
Rate limiting on sensitive endpoints
Exportable audit logs
Frontend (development): http://localhost:5173 Production (via script): http://YOUR_SERVER



syntra/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── routers/
│   │   │   ├── mikrotiks.py
│   │   │   ├── commands.py
│   │   │   └── groups.py
│   │   └── utils.py
│   ├── requirements.txt
│   ├── alembic.ini
│   └── migrations/   (inicial vazio)
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── pages/
│           ├── Login.jsx
│           └── Dashboard.jsx
│
├── scripts/
│   ├── install_syntra.sh
│   └── create_syntra.sh   (novo gerador de estrutura)
│
├── docs/
│   ├── README.md
│   └── architecture.md
│
└── examples/
    └── sample.env
