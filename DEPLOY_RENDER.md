# Deploy no Render - Sistema de Produção

## Pré-requisitos
- Conta no Render (https://render.com)
- Repositório Git com o código (GitHub, GitLab, ou Bitbucket)

## Arquivos de Configuração

O projeto já está configurado com os arquivos necessários para deploy no Render:

- **Procfile**: Define como executar a aplicação
- **runtime.txt**: Especifica a versão do Python (3.11.6)
- **requirements.txt**: Lista todas as dependências necessárias

## Passo a Passo para Deploy

### 1. Preparar o Repositório
```bash
git add .
git commit -m "Preparado para deploy no Render"
git push origin main
```

### 2. Criar Web Service no Render

1. Acesse https://dashboard.render.com
2. Clique em "New +" e selecione "Web Service"
3. Conecte seu repositório Git
4. Configure o serviço:

   **Configurações Básicas:**
   - Name: `sistema-producao` (ou nome de sua preferência)
   - Region: Escolha a região mais próxima
   - Branch: `main` (ou sua branch principal)
   - Root Directory: (deixe em branco)
   
   **Build & Deploy:**
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: (o Render lerá automaticamente do Procfile)

### 3. Variáveis de Ambiente

No painel do Render, em "Environment", adicione as seguintes variáveis:

**Obrigatória:**
- `SECRET_KEY`: Uma chave secreta forte para sessões Flask (gere uma chave aleatória única)
  - Exemplo: `SECRET_KEY=sua_chave_secreta_muito_forte_e_aleatoria_aqui_123456789`

**Opcionais:**
- `DEBUG=false` (já é o padrão, mas pode definir explicitamente)
- Outras variáveis de ambiente que seu sistema precisar

💡 **Dica**: Para gerar uma SECRET_KEY forte:
```python
import secrets
print(secrets.token_hex(32))
```

### 4. Deploy

1. Clique em "Create Web Service"
2. O Render fará o deploy automaticamente
3. Aguarde o processo de build e deploy concluir
4. Sua aplicação estará disponível em: `https://sistema-producao.onrender.com` (ou o nome que você escolheu)

## Configurações de Produção

### Workers do Gunicorn
O Procfile está configurado com 4 workers:
```
web: gunicorn --bind 0.0.0.0:$PORT app:app --workers 4 --timeout 120
```

Para ajustar conforme necessário:
- `--workers 4`: Número de processos workers (recomendado: 2-4 × número de CPUs)
- `--timeout 120`: Timeout em segundos para requisições longas

### Plano Recomendado
- **Starter**: Para uso básico (512 MB RAM, compartilhado)
- **Standard**: Para uso mais intenso (2 GB RAM, dedicado)

## Persistência de Dados

⚠️ **IMPORTANTE**: Este sistema usa arquivos Python (.py) para armazenar dados:
- `Usuario.py`
- `Producoes.py`
- `requisicao.py`
- `feedback.py`
- `Qualidade.py`
- `Notificacao.py`

No Render, os dados serão persistidos apenas enquanto o serviço não for reiniciado. Para produção real, considere:

1. **Solução Rápida**: Usar Render Disks para persistência
   - No painel do Render, adicione um Disk
   - Monte em `/data`
   - Modifique app.py para salvar arquivos em `/data`

2. **Solução Ideal**: Migrar para banco de dados
   - PostgreSQL (Render oferece banco grátis até 1GB)
   - SQLite com Render Disk
   - MongoDB Atlas

## Monitoramento

- Logs: Disponíveis no painel do Render em "Logs"
- Métricas: CPU, memória e requisições no painel "Metrics"
- Health Checks: Configure em "Settings > Health Check Path"

## Troubleshooting

### Erro de Build
- Verifique se `requirements.txt` está correto
- Certifique-se de que `runtime.txt` tem a versão correta do Python

### Erro de Start
- Verifique os logs no painel do Render
- Confirme que o Procfile está no diretório raiz
- Verifique se a porta está sendo lida da variável `PORT`

### Performance Lenta
- Aumente o número de workers no Procfile
- Considere upgrade do plano
- Otimize o código Python

## Atualizações

Para atualizar a aplicação:
```bash
git add .
git commit -m "Atualizações"
git push origin main
```

O Render fará deploy automático a cada push na branch configurada.

## Custos

- **Free Tier**: 750 horas/mês (suspende após 15 min de inatividade)
- **Starter**: $7/mês (sempre ativo)
- **Standard**: $25/mês (2 GB RAM, melhor performance)

Para mais informações: https://render.com/pricing
