-- Create cliente table
CREATE TABLE IF NOT EXISTS cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL,
    endereco TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Create pedido_estado table
CREATE TABLE IF NOT EXISTS pedido_estado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT UNIQUE,
    cliente_telefone TEXT,
    cliente_nome TEXT,
    cliente_endereco TEXT,
    status TEXT NOT NULL DEFAULT 'iniciado',
    itens TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (cliente_telefone) REFERENCES cliente (telefone)
);

-- Create pedido table
CREATE TABLE IF NOT EXISTS pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    estado_id INTEGER NOT NULL,
    total REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'pendente',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente (id),
    FOREIGN KEY (estado_id) REFERENCES pedido_estado (id)
); 