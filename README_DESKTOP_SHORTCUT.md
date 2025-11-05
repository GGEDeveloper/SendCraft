# 🖥️ Atalho do Desktop para SendCraft (Windows + WSL)

Este guia explica como criar um atalho no desktop do Windows para iniciar automaticamente o SendCraft no WSL.

## 📋 Método 1: Usando o Script PowerShell (Recomendado)

1. **No Windows PowerShell**, execute o script de criação de atalho:

```powershell
cd \\wsl$\Ubuntu\home\ggedeveloper\SendCraft
.\create_desktop_shortcut.ps1
```

Ou se estiver no WSL, execute:

```bash
# No WSL
cd /home/ggedeveloper/SendCraft
powershell.exe -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1
```

2. Um atalho chamado **"SendCraft"** será criado no seu desktop do Windows.

3. **Clique duas vezes** no atalho para iniciar o servidor.

## 📋 Método 2: Criação Manual do Atalho

1. **Clique direito** no desktop do Windows → **Novo** → **Atalho**

2. No campo "Local do item", cole:
   ```
   \\wsl$\Ubuntu\home\ggedeveloper\SendCraft\start_sendcraft.bat
   ```
   
   **Nota**: Se sua distribuição WSL não for Ubuntu, substitua "Ubuntu" pelo nome da sua distribuição.

3. Clique em **Próximo**

4. Nomeie como **"SendCraft"**

5. Clique em **Concluir**

6. **Clique direito** no atalho criado → **Propriedades**

7. Em "Iniciar em", cole:
   ```
   \\wsl$\Ubuntu\home\ggedeveloper\SendCraft
   ```

8. Clique em **OK**

## 🎯 Como Usar

1. **Clique duas vezes** no atalho "SendCraft" no desktop
2. Uma janela de terminal será aberta
3. O servidor iniciará automaticamente no WSL
4. Acesse: http://localhost:5000

## ⚙️ Configuração Avançada

### Mudar a Distribuição WSL

Se você usa uma distribuição WSL diferente (não Ubuntu), edite o arquivo `start_sendcraft.bat`:

```batch
REM Substitua "Ubuntu" pelo nome da sua distribuição
wsl -d Debian -e bash -c "cd /home/ggedeveloper/SendCraft && source venv/bin/activate && python3 run_dev.py"
```

Ou especifique explicitamente:

```batch
wsl -d Ubuntu-22.04 -e bash -c "cd /home/ggedeveloper/SendCraft && source venv/bin/activate && python3 run_dev.py"
```

### Verificar Nome da Distribuição WSL

No PowerShell do Windows:
```powershell
wsl --list --verbose
```

### Executar em Background

Se quiser que o servidor execute em background sem janela de terminal, crie uma variante do script que use `wsl.exe` diretamente sem janela.

## 🔧 Troubleshooting

### Erro: "WSL não está disponível"
- Instale o WSL: `wsl --install`
- Ou verifique se está habilitado: `wsl --status`

### Erro: "Caminho não encontrado"
- Verifique se o caminho `/home/ggedeveloper/SendCraft` existe no WSL
- Use `wsl -e pwd` para verificar o caminho atual

### Erro: "venv não encontrado"
- Execute no WSL: `cd /home/ggedeveloper/SendCraft && python3 -m venv venv`
- Ative o venv: `source venv/bin/activate`
- Instale dependências: `pip install -r requirements.txt`

### Atalho não funciona
- Verifique se o caminho usa `\\wsl$\Ubuntu\...` (com barras invertidas duplas)
- Certifique-se de que a distribuição WSL está em execução
- Tente executar o `.bat` diretamente primeiro para verificar erros

## 📝 Arquivos Criados

- `start_sendcraft.bat` - Script batch para Windows
- `start_sendcraft.ps1` - Script PowerShell alternativo
- `create_desktop_shortcut.ps1` - Script para criar atalho automaticamente

