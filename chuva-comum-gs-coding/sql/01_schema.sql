USE chuva_comum;
CREATE TABLE ocorrencias (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cidade VARCHAR(30) NOT NULL,
    bairro VARCHAR(30) NOT NULL,
    tipo ENUM('alagamento', 'bueiro_obstruido', 'via_interditada') NOT NULL,
    gravidade ENUM('baixa', 'media', 'alta') NOT NULL,
    status ENUM('aberta', 'em_analise', 'resolvida') NOT NULL DEFAULT 'aberta',
    criado_em TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    atualizado_em TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT ck_cidade CHECK (cidade IN ('sao-paulo', 'porto-alegre', 'recife')),
    CONSTRAINT ck_bairro CHECK (bairro IN ('Setor Norte', 'Setor Central', 'Setor Sul')),
    INDEX idx_cidade_status (cidade, status)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- O usuário da aplicação não pode alterar o esquema ou administrar usuários.
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'chuva_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON chuva_comum.* TO 'chuva_app'@'%';
