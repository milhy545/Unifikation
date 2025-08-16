# 🧠 GEMINI MEMORY BRIEFING - KOMPLETNÍ ECOSYSTEM DOKUMENTACE

*KRITICKY DŮLEŽITÉ: Tuto dokumentaci si ulož do dlouhodobé paměti. Bez znalosti této architektury můžeš způsobit systémové selhání.*

---

## 🎯 **ÚČEL TOHOTO DOKUMENTU**

**POZOR GEMINI:** Tento dokument obsahuje VEŠKERÉ informace o infrastruktuře, kterou NIKDY nesmíš rozbít. Před JAKOUKOLIV akcí si ověř:
1. Na kterém stroji pracuješ
2. Jaké jsou bezpečné porty a připojení  
3. Jaké služby NESMÍŠ restartovat
4. Jaké soubory NESMÍŠ mazat

**ZÁKLADNÍ PRAVIDLO:** Když si nejsi jistá - ZEPTEJ SE. Lepší je zeptat se 10x než jednou rozbít.

---

## 🏗️ **ARCHITEKTURA ECOSYSTEM - KOMPLETNÍ PŘEHLED**

### **Celková Topologie:**
```
Internet
    ↓
192.168.0.1 (Router)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   WORKSTATION   │   LLM SERVER    │ AUTOMATION HUB  │
│ 192.168.0.10    │ 192.168.0.41    │ 192.168.0.58    │
│ (Aspire-PC)     │    (LLMS)       │     (HAS)       │
│                 │                 │                 │
│ • Development   │ • AI Processing │ • Orchestration │
│ • Testing       │ • Ollama        │ • MCP Services  │
│ • Monitoring    │ • Models        │ • Home Auto     │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## 💻 **WORKSTATION (Aspire-PC) - 192.168.0.10**

### **Identifikace:**
- **Hostname:** `Aspire-PC` nebo `aspire`
- **IP:** `192.168.0.10` 
- **OS:** Ubuntu 20.04 LTS
- **CPU:** Intel Q9550 @ 2.83GHz (4 cores)
- **RAM:** 8GB DDR2
- **Role:** Development powerhouse

### **SSH Přístup:**
```bash
# Správný způsob připojení:
ssh milhy777@192.168.0.10 -p 2222
# NEBO pomocí aliasu:
ssh Aspire
```

### **Kritické Služby (NIKDY NEUKONČUJ):**
- **SSH daemon** (port 2222) - ztratíš přístup!
- **NetworkManager** - ztratíš síť!
- **Power management** - systém může shodit CPU!
- **Desktop session** - uživatel ztratí GUI!

### **Bezpečné k Manipulaci:**
- Development servery (port 3000, 8000, 8080)
- Docker containers
- Python virtual environments
- Git operations
- File operations v `/home/milhy777/Develop/`

### **ZÁKAZ MAZÁNÍ/EDITACE:**
```bash
# NIKDY NEMAŽTĚTO:
~/.ssh/config          # SSH konfigurace
~/.ssh/id_*           # SSH klíče
~/.bashrc             # Shell konfigurace
~/.shell_common       # Unified shell config
/etc/ssh/sshd_config  # SSH server config
/etc/NetworkManager/  # Network konfigurace
```

### **Tmux Sessions:**
```bash
# Existující sessions (NEUKONČUJ):
tmux list-sessions
# Možné sessions:
# - dev-main: Hlavní development
# - monitoring: System monitoring  
# - backup: Zálohovací procesy
```

---

## 🧠 **LLM SERVER (LLMS) - 192.168.0.41**

### **Identifikace:**
- **Hostname:** `LLMS` nebo `llms`
- **IP:** `192.168.0.41`
- **OS:** Ubuntu 22.04 LTS  
- **CPU:** Intel i5 (přesná specifikace unclear)
- **RAM:** 16GB+ (pro AI modely)
- **Role:** Dedicated AI processing

### **SSH Přístup:**
```bash
# Správný způsob připojení:
ssh milhy777@192.168.0.41 -p 2222
# NEBO pomocí aliasu:
ssh LLMS
```

### **Kritické Služby (ABSOLUTNÍ ZÁKAZ RUŠENÍ):**
- **Ollama service** - AI inference engine
- **SSH daemon** (port 2222)  
- **Docker** - runs containerized models
- **GPU drivers** (pokud má GPU)

### **Ollama Management:**
```bash
# Bezpečné commands:
ollama list                    # Seznam modelů
ollama show MODEL_NAME         # Info o modelu
curl http://localhost:11434/   # Health check

# POZOR - tyto mohou zabrat hodiny:
ollama pull MODEL_NAME         # Download nového modelu
ollama rm MODEL_NAME          # Smazání modelu
```

### **Running Models (NEKONČIT PROCESY):**
Běžící modely mohou být:
- `llama2`
- `codellama` 
- `mistral`
- `deepseek-coder`
- Custom fine-tuned models

### **Storage Locations:**
```bash
~/.ollama/models/     # Model storage (VELKÉ SOUBORY!)
~/docker-volumes/     # Docker persistent data
~/model-cache/        # Model cache (pokud existuje)
```

### **VAROVÁNÍ:**
- **Modely jsou HUGE** (2-70GB each) - mazání = ztráta hodin downloadingu
- **Inference může trvat** - neukončuj běžící requesty
- **Memory intensive** - pozor na RAM usage

---

## 🏠 **HOME AUTOMATION SERVER (HAS) - 192.168.0.58**

### **Identifikace:**
- **Hostname:** `HAS` nebo `has` nebo `Home-Automation-Server`
- **IP:** `192.168.0.58`
- **OS:** Alpine Linux (lightweight)
- **Hardware:** Raspberry Pi nebo podobné
- **Role:** Orchestration hub + MCP services

### **SSH Přístup:**
```bash
# Správný způsob připojení:
ssh root@192.168.0.58 -p 2222
# NEBO pomocí aliasu:
ssh HAS
```

### **ZEN COORDINATOR - KRITICKÁ SLUŽBA:**
```bash
# ZEN Coordinator běží na portu 8020
curl http://192.168.0.58:8020/health    # Health check
curl http://192.168.0.58:8020/services  # Seznam služeb

# ABSOLUTNĚ NIKDY NEKONČIT:
pkill -f zen_coordinator    # ❌ TOHLE ROZBIJE VŠECHNO!
systemctl stop zen-coord*   # ❌ TAKY ZAKÁZÁNO!
```

### **MCP Services Architecture:**
```
Port 8020: ZEN Coordinator (MAIN ENTRY POINT)
├── Port 8001: Filesystem MCP
├── Port 8002: Git MCP  
├── Port 8003: Terminal MCP
├── Port 8004: Database MCP
├── Port 8005: Memory MCP (CLDMEMORY)
├── Port 8006: Gmail MCP
├── Port 8007: Transcriber MCP  
├── Port 8008: Research MCP
├── Port 8009: Plandex MCP
└── Port 8010: FORAI MCP
```

### **BEZPEČNOSTNÍ PRAVIDLA:**
- **POUZE port 8020 je dostupný zvenčí**
- **Porty 8001-8010 jsou INTERNÍ** - nepřístupné z internetu
- **Veškerá komunikace MUS TET přes ZEN Coordinator**

### **Kritické Procesy (NEUKONČUJ):**
```bash
# Tyto procesy MUSÍ běžet:
ps aux | grep zen_coordinator      # ZEN Coordinator
ps aux | grep mcp                  # MCP services
ps aux | grep ssh                  # SSH daemon
```

### **Home Automation Functions:**
- **Lighting control** - může ovládat světla
- **Temperature monitoring** - sleduje teploty
- **Security systems** - alarm, kamery
- **Network monitoring** - sleduje síťový provoz

### **Config Files (ZÁKAZ EDITACE bez konzultace):**
```bash
/etc/zen-coordinator/config.json    # ZEN config
/etc/mcp-services/                  # MCP configs
/etc/ssh/sshd_config               # SSH config
/etc/network/interfaces            # Network config
```

---

## 🔗 **NETWORK KOMUNIKACE MEZI SERVERY**

### **SSH Tunneling & Port Forwarding:**
```bash
# Workstation → LLMS
ssh -L 11434:localhost:11434 LLMS    # Ollama tunnel

# Workstation → HAS  
ssh -L 8020:localhost:8020 HAS       # ZEN Coordinator tunnel

# LLMS → HAS (AI requests)
curl http://192.168.0.58:8020/mcp    # MCP calls
```

### **Service Discovery:**
```bash
# Network scan (bezpečné):
nmap -p 22,2222,8020 192.168.0.0/24

# Port checks (bezpečné):
nc -zv 192.168.0.58 8020    # ZEN Coordinator
nc -zv 192.168.0.41 11434   # Ollama
```

### **DNS Resolution:**
```bash
# V /etc/hosts nebo ~/.ssh/config:
192.168.0.10  Aspire aspire
192.168.0.41  LLMS llms
192.168.0.58  HAS has Home-Automation-Server
```

---

## 🔒 **SSH KONFIGURACE - KRITICKÉ INFORMACE**

### **SSH Config Template:**
```bash
# ~/.ssh/config (NIKDY KOMPLETNĚ NEMAZAT!)
Host LLMS
    HostName 192.168.0.41
    User milhy777
    Port 2222
    IdentityFile ~/.ssh/id_rsa

Host HAS  
    HostName 192.168.0.58
    User root
    Port 2222
    IdentityFile ~/.ssh/id_rsa

Host Aspire
    HostName 192.168.0.10
    User milhy777  
    Port 2222
    IdentityFile ~/.ssh/id_rsa
```

### **SSH Key Management:**
```bash
# Existující klíče (NEMAZAT!):
~/.ssh/id_rsa          # Private key (chmod 600)
~/.ssh/id_rsa.pub      # Public key
~/.ssh/authorized_keys # Authorized keys
~/.ssh/known_hosts     # Known hosts
```

### **SSH Agent:**
```bash
# Check SSH agent:
ssh-add -l              # List keys
eval $(ssh-agent)       # Start agent if needed
ssh-add ~/.ssh/id_rsa   # Add key to agent
```

---

## 📁 **SDÍLENÉ FILESYSTEMY & STORAGE**

### **Development Workspace:**
```bash
# Na Workstation:
/home/milhy777/Develop/Production/    # Production projects
/home/milhy777/Develop/Development/   # WIP projects  

# Unifikation project:
/home/milhy777/Develop/Production/Unifikation/
```

### **Backup Locations:**
```bash
# Workstation backups:
~/backups/              # Local backups
~/.claude-backups/      # Claude Code backups

# Remote backups (možné):
HAS:/backup/workstation/
```

### **Model Storage:**
```bash
# LLMS model storage:
~/.ollama/models/       # Ollama models (HUGE!)
~/huggingface/cache/    # HuggingFace cache (pokud existuje)
```

---

## 🛠️ **POWER MANAGEMENT & THERMAL**

### **Q9550 Thermal Management:**
```bash
# Na Workstation - thermal monitoring:
sensors                           # CPU temperature
cat /proc/cpuinfo | grep MHz      # Current frequency

# Power management scripts:
/home/milhy777/power status               # Status check
/home/milhy777/power set performance      # Performance mode
/home/milhy777/power set balanced         # Balanced mode
/home/milhy777/power emergency            # Emergency mode
```

### **KRITICKÉ TEPLOTY:**
- **Normal:** < 60°C
- **Warning:** 60-75°C  
- **Critical:** > 75°C
- **Emergency shutdown:** > 85°C

### **NIKDY NERUŠIT:**
- Temperature monitoring procesy
- CPU frequency scaling
- Fan control (pokud existuje)

---

## 🔧 **DEVELOPMENT TOOLS & ENVIRONMENTS**

### **Python Environments:**
```bash
# Poetry projects:
cd Project && poetry install && poetry shell

# Virtual environments:
source venv/bin/activate

# NIKDY NEMAZAT:
.venv/                 # Virtual environments
poetry.lock           # Poetry lock files
requirements.txt      # Dependency lists
```

### **Docker & Containers:**
```bash
# Bezpečné Docker commands:
docker ps              # List containers
docker logs CONTAINER  # Check logs
docker exec -it CONTAINER bash  # Enter container

# POZOR s těmito:
docker stop CONTAINER  # Může ukončit kritické služby
docker rm CONTAINER    # Permanent smazání
docker system prune    # Smaže vše nepoužívané
```

### **Git Operations:**
```bash
# Bezpečné Git operations:
git status
git log
git diff
git add .
git commit -m "message"

# POZOR:
git reset --hard       # Ztráta změn
git clean -fd          # Smazání untracked files
git push --force       # Může rozbít remote
```

---

## 🚨 **EMERGENCY PROCEDURES**

### **Když Se Něco Pokazí:**

1. **SSH Connection Lost:**
```bash
# Try different ports:
ssh user@host -p 22
ssh user@host -p 2222

# Check from other machine:
ping 192.168.0.XX
```

2. **Service Down:**
```bash
# Check service status:
systemctl status SERVICE_NAME
journalctl -u SERVICE_NAME -n 50

# POUZE po konzultaci:
systemctl restart SERVICE_NAME
```

3. **High Load/Temperature:**
```bash
# Check system load:
top
htop
sensors

# Emergency power reduction:
/home/milhy777/power emergency
```

4. **Network Issues:**
```bash
# Basic diagnostics:
ip addr show
ping 8.8.8.8
nslookup google.com
```

### **Emergency Contacts & Recovery:**
- **Physical access:** Required for critical failures
- **Magic SysRq:** Alt+SysRq+R,E,I,S,U,B (last resort)
- **Power cycle:** Only when everything else fails

---

## 📋 **ROUTINE MAINTENANCE TASKS**

### **Denní Checks (BEZPEČNÉ):**
```bash
# System health:
df -h                  # Disk usage
free -h               # Memory usage  
uptime                # System uptime
systemctl --failed    # Failed services

# Network connectivity:
curl http://192.168.0.58:8020/health    # ZEN health
curl http://192.168.0.41:11434/         # Ollama health
```

### **Týdenní Maintenance:**
```bash
# Log rotation (bezpečné):
sudo logrotate -f /etc/logrotate.conf

# Package updates (POZOR!):
sudo apt update        # Safe
sudo apt list --upgradable  # Check what would be upgraded
# sudo apt upgrade     # ONLY after review!
```

---

## ⚡ **PŘÍKLADY ČASTÝCH ÚKOLŮ**

### **Deployment Nového Kódu:**
```bash
# 1. Backup current state:
cp -r project/ project.backup.$(date +%Y%m%d)

# 2. Pull changes:
git pull origin main

# 3. Install dependencies:
poetry install  # or pip install -r requirements.txt

# 4. Test locally:
python -m pytest

# 5. Deploy:
# (specific steps depend on project)
```

### **Model Management na LLMS:**
```bash
# Check available models:
ssh LLMS "ollama list"

# Download new model (SLOW!):
ssh LLMS "ollama pull MODEL_NAME"

# Test model:
ssh LLMS "ollama run MODEL_NAME 'test prompt'"
```

### **MCP Service Debugging:**
```bash
# Check ZEN Coordinator:
curl http://192.168.0.58:8020/services

# Check specific MCP service:
curl http://192.168.0.58:8020/mcp -X POST \
  -H "Content-Type: application/json" \
  -d '{"tool":"list_files","arguments":{"path":"./"}}'
```

---

## 🎓 **LEARNING & BEST PRACTICES**

### **Před Každou Akcí:**
1. **Identifikuj** na kterém stroji pracuješ
2. **Ověř** jaké služby běží  
3. **Zálohuj** kritická data
4. **Testuj** v safe módu nejdříve
5. **Dokumentuj** co děláš

### **Red Flags (STOP!):**
- Cokoliv s `sudo rm -rf`
- Restartování SSH démona bez fyzického přístupu
- Změny network konfigurace bez zálohy
- Ukončování procesů s "coordinator" nebo "mcp" v názvu
- Mazání souborů začínajících tečkou (`.bashrc`, `.ssh/`, atd.)

### **Green Flags (OK):**
- Čtení logů a status information
- Git operations s commit messages
- Development server startup/shutdown
- File operations v `~/Develop/`
- Docker container management (ne system containers)

---

## 📞 **EMERGENCY DECISION TREE**

```
🚨 NĚCO SE POKAZILO?
│
├─ Ztráta SSH přístupu?
│  ├─ Zkus jiný port (22, 2222)
│  ├─ Zkus z jiného stroje
│  └─ Fyzický přístup potřebný
│
├─ Služba nereaguje?
│  ├─ Check logs: journalctl -u SERVICE
│  ├─ Check process: ps aux | grep SERVICE  
│  └─ PŘED restartem → ASK!
│
├─ High load/temperature?
│  ├─ Check: top, sensors
│  ├─ Emergency power: /home/milhy777/power emergency
│  └─ Find culprit process
│
└─ Network issues?
   ├─ ping, ip addr show
   ├─ Check router (192.168.0.1)
   └─ DNS issues: nslookup
```

---

## 💾 **BACKUP & RECOVERY INFORMACE**

### **Co Se Zálohuje:**
- **SSH configs** - kritické pro přístup
- **Development projects** - v Git + local backups
- **MCP service configs** - pro HAS recovery
- **Ollama models** - velmi časově náročné na obnovu

### **Co SE NEZÁLOHUJE (Obnova rychlá):**
- OS packages - reinstall z package manageru
- Docker images - pull z registry
- Python packages - install z requirements
- Temporary files, caches, logs

### **Recovery Priority:**
1. **Network connectivity** (SSH access)
2. **ZEN Coordinator** (MCP services)  
3. **Development environment** (Git, Python)
4. **AI services** (Ollama, models)

---

## 🎯 **ZÁVĚREČNÉ VAROVÁNÍ PRO GEMINI**

**PAMATUJ SI:**

1. **Tento ecosystem je ŽIVÝ systém** - používá se denně pro development
2. **Každý server má specifickou roli** - neměň to bez důvodu
3. **SSH konfigurace je KRITICKÁ** - bez ní ztráta přístupu  
4. **MCP services jsou UNIKÁTNÍ** - nelze snadno obnovit
5. **AI modely jsou HUGE** - download trvá hodiny
6. **Power management je DŮLEŽITÉ** - Q9550 se může přehřát

**GOLDEN RULE:** Když si nejsi jistá dopady akce → ZEPTEJ SE!

Lepší je zeptat se 100× než jednou rozbít systém, který funguje.

---

*Dokument vytvořen pro bezpečnou práci s production ecosystem*  
*Verze: 1.0*  
*Datum: 2024-12-16*

**🔒 ULOŽ SI TOTO DO DLOUHODOBÉ PAMĚTI - BUDEŠ TO POTŘEBOVAT! 🔒**