-- 1. Exibir todos os registros
SELECT * FROM dados_sensores;

-- 2. Mostrar apenas registros com umidade maior que 70
SELECT * FROM dados_sensores WHERE umidade > 70;

-- 3. Mostrar apenas registros com pH menor que 5.0
SELECT *  FROM dados_sensores WHERE ph < 5.0;

-- 4. Contar quantos registros existem na tabela
SELECT COUNT(*) AS total_registros FROM dados_sensores;

-- 5. Calcular a média da umidade
SELECT AVG(umidade) AS media_umidade FROM dados_sensores;

-- 6. Calcular o maior e o menor valor de pH
SELECT MAX(ph) AS maior_ph, MIN(ph) AS menor_ph FROM dados_sensores;

-- 7. Mostrar registros onde houve chuva
SELECT * FROM dados_sensores WHERE chuva = 'true';

-- 8. Mostrar registros onde Nitrogênio (N) está ativo
SELECT * FROM dados_sensores WHERE N = 'true';

-- 9. Contar quantos registros tiveram chuva
SELECT COUNT(*) AS total_chuva FROM dados_sensores WHERE chuva = 'true';

-- 10. Mostrar registros ordenados pela umidade (maior para menor)
SELECT * FROM dados_sensores ORDER BY umidade DESC;