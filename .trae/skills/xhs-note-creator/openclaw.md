# OpenClaw 本地部署保姆级教程

> 全程保姆喂饭级指引，每个操作都标注"点击哪里、复制什么、粘贴到哪里"，包含可直接复用的代码命令、异常排查方案，不改变原意、不添加冗余内容，哪怕是完全不懂电脑技术、不懂代码的纯新手，跟着做也能零踩坑，轻松拥有专属私人AI助理。

本文基于2026年2月OpenClaw最新稳定版（v2026.2.2-cn）、OpenClaw中国社区实测数据及新手高频踩坑反馈，全网整合最优流程重写，兼顾本地部署（零成本首选），重点拆解本地部署每一个细节，10分钟内搞定部署，开启AI自动化办公、日常辅助的便捷体验。

---

## 一、核心前提：打破误区，明确两种部署方式的区别（新手必看）

在开始部署前，先明确本地部署与上一篇阿里云简单部署的核心区别，根据自身需求选择，避免盲目操作，两种方式均适配2026年最新版OpenClaw，新手无需纠结技术细节，按需选择即可：
![alt text](image.png)
---

## 二、本地部署：零成本，10分钟搞定（新手首选，全程保姆级）

本地部署是最适合新手的方式，全程免费、操作极简，无需购买云服务器、无需开通任何付费服务，只要有一台普通电脑，跟着以下步骤操作，10分钟就能完成部署，开启私人AI助理之旅。全程分为"前置准备、环境配置、OpenClaw部署、验证使用、基础优化"5个步骤，每个步骤都有详细指引，代码可直接复制复用，零代码基础也能轻松搞定。

### （一）前置准备（1分钟搞定，零难度）

无需下载复杂工具，仅需准备2件事，确保后续部署不中断，新手必做：

#### 1. 电脑配置检查（必做）

确认电脑满足最低要求（无需高端配置），具体如下：

| 配置项 | 最低要求 | 说明 |
|--------|---------|------|
| **CPU** | Intel i3 4代+/AMD Ryzen 3 2000+ | 支持虚拟化，需在BIOS中开启，步骤见常见坑1 |
| **内存** | 最低2GiB（建议4GiB） | 开启轻量化配置可适配2GiB |
| **存储** | 最低40GiB SSD | 机械硬盘需优化读写，步骤见下文 |
| **系统** | Windows 10 64位+/MacOS 12+/Linux（Ubuntu 20.04 LTS+） | Windows 7不兼容，请勿尝试 |
| **网络** | 仅部署时需要联网 | 下载依赖包，部署完成后基础功能（如对话、本地文件处理）无需联网 |

#### 2. 必备工具下载（零难度，直接点击下载）

**核心依赖：**

- **Node.js v22+**（必须≥v22.0.0，国内镜像下载，无需手动配置环境变量）
- **Git**（用于下载OpenClaw代码，国内镜像适配版）
- **pnpm**（强制推荐，npm在处理依赖树时可能会卡死，部署时自动安装）
- **Ollama v0.15.4+**（可选，用于本地运行大模型，无需对接第三方API，新手可先跳过，后续补充）

**下载地址（国内镜像，高速下载，避免超时）：**

| 工具 | Windows下载链接 | Mac下载链接 |
|------|---------------|-----------|
| **Node.js v22+** | [下载MSI](https://registry.npmmirror.com/binary.html?path=node/v22.0.0/node-v22.0.0-x64.msi) | [下载PKG](https://registry.npmmirror.com/binary.html?path=node/v22.0.0/node-v22.0.0.pkg) |
| **Git** | [下载EXE](https://registry.npmmirror.com/binary.html?path=git-for-windows/v2.43.0.windows.1/Git-2.43.0-64-bit.exe) | [App Store下载](https://git-scm.com/download/mac) |
| **Ollama** | [官网下载](https://ollama.com/download) | [官网下载](https://ollama.com/download) |

---

### （二）环境配置（3分钟搞定，复制粘贴代码即可）

这一步是本地部署的核心，主要安装并配置Node.js、Git、pnpm，全程复制粘贴代码，无需手动操作，分Windows、Mac/Linux两种系统，新手根据自己的电脑系统选择对应步骤，不要混淆。

#### 1. Windows系统（优先WSL2，无WSL2则用原生系统，新手首选原生）

**操作步骤：**

打开电脑，以**管理员身份**打开PowerShell（按下Win+X，选择"Windows PowerShell（管理员）"），然后依次复制以下代码，粘贴到PowerShell中，每粘贴一行，按一次回车键执行，全程无需修改任何内容，耐心等待执行完成即可（执行速度取决于网络，一般3分钟内搞定）。

```bash
# 1. 配置系统执行权限（避免后续安装失败）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
Get-ExecutionPolicy -List # 验证，LocalMachine显示RemoteSigned即为成功

# 2. 安装Node.js v22+（静默安装，避免弹窗，已下载安装包可跳过此步）
iwr -useb https://registry.npmmirror.com/binary.html?path=node/v22.0.0/node-v22.0.0-x64.msi -OutFile node-v22.0.0-x64.msi
.\node-v22.0.0-x64.msi /quiet

# 3. 验证Node.js安装成功（输出v22.0.0+即为成功）
node -v
npm -v # 验证npm，输出10.5.0+即为成功

# 4. 配置npm国内镜像（解决下载慢、超时问题，关键步骤）
npm config set registry https://registry.npmmirror.com
npm config set puppeteer_download_host https://registry.npmmirror.com/binary.html?path=chromium-browser-snapshots/

# 5. 安装Git（静默安装，已下载安装包可跳过此步）
iwr -useb https://registry.npmmirror.com/binary.html?path=git-for-windows/v2.43.0.windows.1/Git-2.43.0-64-bit.exe -OutFile Git-2.43.0-64-bit.exe
.\Git-2.43.0-64-bit.exe /silent /norestart

# 6. 验证Git安装成功（输出git version 2.43.0+即为成功）
git --version

# 7. 安装pnpm（核心包管理器，必须安装）
npm install -g pnpm

# 8. 验证pnpm安装成功（输出9.0.0+即为成功）
pnpm -v

# 9. 安装Ollama（本地模型核心，可选，新手可跳过）
winget install ollama # 若无winget，手动双击下载的安装包安装
ollama --version # 验证，输出0.15.4+即为成功

# 10. 配置pip国内镜像（后续安装依赖用，提前配置）
mkdir %APPDATA%\pip
echo "[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 60" > %APPDATA%\pip\pip.ini
pip install pip -U # 升级pip，验证镜像配置
```

#### 2. Mac/Linux系统（含WSL2，轻量化首选，操作更简洁）

**操作步骤：**

打开电脑的"终端"（Mac按下Command+空格，输入"终端"打开；Linux直接打开终端），依次复制以下代码，粘贴到终端中，每粘贴一行，按一次回车键执行，全程无需修改，3分钟内即可完成。

```bash
# 1. 更新系统依赖（跳过无关更新，加速执行）
sudo apt update && sudo apt install -y curl git build-essential --no-install-recommends # Linux专用
# Mac专用更新命令：brew update（若未安装brew，先执行/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"）

# 2. 安装Node.js v22+（国内镜像，一键安装，无需手动配置环境变量）
curl -fsSL https://registry.npmmirror.com/binary.html?path=node/v22.0.0/node-v22.0.0-linux-x64.tar.xz | sudo tar -xJ -C /usr/local/ # Linux专用
# Mac专用安装命令：curl -fsSL https://registry.npmmirror.com/binary.html?path=node/v22.0.0/node-v22.0.0.pkg -o node-v22.0.0.pkg && sudo installer -pkg node-v22.0.0.pkg -target /

# 3. 配置Node.js环境变量（Linux专用，Mac可跳过）
echo "export PATH=/usr/local/node-v22.0.0-linux-x64/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc

# 4. 验证Node.js安装成功（输出v22.0.0+即为成功）
node -v
npm -v # 验证npm，输出10.5.0+即为成功

# 5. 配置npm国内镜像（解决下载慢、超时，关键步骤）
npm config set registry https://registry.npmmirror.com
npm config set puppeteer_download_host https://registry.npmmirror.com/binary.html?path=chromium-browser-snapshots/

# 6. 安装Git（若已安装，可跳过此步）
sudo apt install -y git # Linux专用
# Mac专用安装命令：brew install git（或手动下载安装包）

# 7. 验证Git安装成功
git --version

# 8. 安装pnpm（核心包管理器，必须安装）
npm install -g pnpm

# 9. 验证pnpm安装成功（输出9.0.0+即为成功）
pnpm -v

# 10. 安装Ollama（本地模型核心，可选，新手可跳过）
curl -fsSL https://ollama.com/install.sh | sh # Linux/Mac通用
ollama --version # 验证，输出0.15.4+即为成功

# 11. 安装Python 3.10（兼容最佳版本，避免依赖冲突）
sudo apt install -y python3.10 python3.10-pip python3.10-venv --no-install-recommends # Linux专用
# Mac专用安装命令：brew install python@3.10
python3 --version # 验证，输出Python 3.10.11+即为成功
```

#### 环境配置验证（必做，避免后续部署失败）

执行完以上所有代码后，依次输入以下3条命令，验证环境是否配置成功，若全部输出对应版本号，说明环境配置无误，可进入下一步；若提示"command not found"，重新执行对应安装命令即可。

```bash
# 无论Windows还是Mac/Linux，均执行以下命令（Windows在PowerShell中执行）
node -v # 输出v22.0.0+
git --version # 输出git version 2.43.0+
pnpm -v # 输出9.0.0+
```

---

### （三）OpenClaw本地部署（5分钟搞定，全程复制粘贴，零代码）

环境配置完成后，进入核心部署步骤，全程5分钟左右，主要是下载OpenClaw代码、安装依赖、启动服务，步骤极简，新手跟着操作即可，分Windows、Mac/Linux两种系统，代码通用，仅部分路径略有差异，无需担心。

#### 步骤1：下载OpenClaw代码（国内镜像，高速下载）

打开PowerShell（Windows）或终端（Mac/Linux），复制以下代码，粘贴后按回车键执行，自动从Gitee国内镜像仓库下载代码，避免海外仓库下载超时（新手无需修改任何内容）：

```bash
# 1. 克隆OpenClaw国内镜像仓库（高速下载，避免超时）
git clone https://gitee.com/OpenClaw-CN/openclaw-cn.git

# 2. 进入OpenClaw代码目录（必须进入该目录，否则后续命令无法执行）
cd openclaw-cn

# 3. 切换到2026年最新稳定版分支（v2026.2.2-cn，最稳定，避免开发版bug）
git checkout v2026.2.2-cn

# 4. 查看当前分支（验证是否切换成功，输出v2026.2.2-cn即为成功）
git branch
```

#### 步骤2：配置国内加速，安装依赖（关键步骤，避免下载超时）

继续在当前目录（openclaw-cn）下，复制以下代码，依次执行，配置pnpm国内镜像，安装OpenClaw所需的全部依赖，全程自动完成，无需手动干预，耐心等待即可（执行速度取决于网络，一般2-3分钟）：

```bash
# 1. 配置pnpm国内镜像（关键，加速依赖下载，避免超时）
pnpm config set registry https://registry.npmmirror.com/

# 2. 安装OpenClaw全部依赖（自动下载，无需手动选择）
pnpm install

# 3. 构建前端界面（首次运行需要编译，后续无需重复执行）
pnpm ui:build

# 4. 构建核心服务（编译后端核心，确保服务能正常启动）
pnpm build
```

#### 步骤3：启动初始化向导，配置基础参数（零难度，交互式操作）

依赖安装完成后，执行初始化向导，自动配置基础参数，无需手动修改，新手只需按提示操作即可，代码直接复制执行：

```bash
# 启动OpenClaw交互式初始化向导（自动配置，新手首选）
pnpm openclaw onboard --install-daemon
```

#### 步骤4：启动OpenClaw服务（最后一步，部署完成）

初始化完成后，继续在当前目录下，复制以下代码，粘贴后按回车键执行，启动OpenClaw网关服务，无需手动操作，启动成功后即可使用：

```bash
# 启动OpenClaw网关服务（默认端口18789，无需修改）
node openclaw.mjs gateway --port 18789 --verbose

# 若关闭终端后，想再次启动服务，重新执行该命令即可
# 若想打开OpenClaw管理面板，执行以下命令（可选）
node openclaw.mjs dashboard
```

> **启动成功的标志：** 终端输出**"Gateway started successfully on http://127.0.0.1:18789"**，此时OpenClaw本地部署已全部完成，无需再执行任何命令，直接进入验证使用步骤。

---

### （四）验证使用（1分钟搞定，零代码，感受AI助理魅力）

部署完成后，快速验证OpenClaw是否能正常使用，全程鼠标点击，无需代码，新手可直接体验私人AI助理的便捷性：

1. 打开浏览器（Chrome/Edge均可），在地址栏中输入"http://127.0.0.1:18789"，按回车键，自动跳转至OpenClaw Web控制台（全中文界面，新手无压力）；

2. 首次进入控制台，无需登录，直接进入对话界面，在输入框中发送简单指令（如"生成一句早安问候语""帮我在桌面上创建一个名为hello_openclaw.txt的文件，并在里面写入：大道至简，实战落地""介绍一下你自己"）；

3. 点击【发送】，等待1-2秒，OpenClaw会自动生成回复，或执行对应操作（如创建文件），若能正常收到回复、完成操作，说明本地部署成功，私人AI助理已正式可用；

4. 测试基础技能：发送指令"现在有哪些可用的Skills？"，OpenClaw会返回当前已集成的基础技能（如文件管理、对话生成），后续可安装更多技能，拓展AI助理能力（步骤见下文）。

---

### （五）本地部署基础优化（可选，新手可后续学习，提升使用体验）

部署完成后，可执行以下优化操作，提升OpenClaw运行速度，避免卡顿、闪退，代码可直接复制复用，适合有进阶需求的新手：

```bash
# 1. 限制OpenClaw内存占用（避免占用过高导致电脑卡顿，新手推荐设置2048MB，2GiB内存）
node openclaw.mjs gateway --port 18789 --memory-limit 2048 --verbose

# 2. 设置OpenClaw开机自启（Windows系统，管理员身份执行）
New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "OpenClaw" -Value "node C:\Users\你的用户名\openclaw-cn\openclaw.mjs gateway --port 18789"

# 3. 设置OpenClaw开机自启（Mac/Linux系统）
echo "node ~/openclaw-cn/openclaw.mjs gateway --port 18789 &" >> ~/.bashrc
source ~/.bashrc

# 4. 清理OpenClaw运行日志（释放磁盘空间，定期执行）
rm -rf ~/.openclaw/logs/*.log # Mac/Linux
# Windows系统清理命令：rm -rf %USERPROFILE%\.openclaw\logs\*.log

# 5. 安装基础Skills（拓展AI助理能力，如文件处理、文本总结）
pnpm openclaw skills install file-manager summary

# 6. 查看已安装技能
pnpm openclaw skills list
```

---

## 三、本地部署常见异常排查（新手必看，遇到问题直接查）

新手本地部署时，可能会遇到"环境配置失败""服务启动失败""控制台无法访问"等问题，无需慌张，以下是最常见的6个问题，每个问题都附原因+解决方案，代码可直接复制复用，跟着操作就能解决，零技术基础也能搞定。

---

### 问题1：执行"node -v"提示"command not found"（Node.js安装失败）

**原因：** 安装包未正确安装、环境变量未配置成功

**解决方案：** 重新执行对应系统的Node.js安装命令，安装完成后，重新配置环境变量（Linux/Mac执行`source ~/.bashrc`，Windows重启PowerShell），再次验证即可。

---

### 问题2：执行"pnpm install"提示"下载超时/依赖安装失败"

**原因：** 网络不稳定、未配置国内镜像、防火墙拦截

**解决方案（代码直接复制）：**

```bash
# 1. 重新配置pnpm国内镜像
pnpm config set registry https://registry.npmmirror.com/

# 2. 清理npm缓存，重新安装依赖
npm cache clean --force
pnpm install --force

# 3. 若仍失败，关闭电脑防火墙，重新执行安装命令
# Windows关闭防火墙：控制面板→系统和安全→Windows Defender防火墙→关闭
# Mac/Linux关闭防火墙：sudo ufw disable
```

---

### 问题3：启动服务时，提示"端口18789被占用"

**原因：** 其他应用正在使用18789端口，导致OpenClaw无法启动

**解决方案（代码直接复制）：**

```bash
# Windows系统（PowerShell中执行）：查找并杀死占用端口的进程
netstat -ano | findstr :18789 # 找到进程ID（PID），复制PID
taskkill /f /pid 进程ID # 替换为找到的PID，杀死进程

# Mac/Linux系统（终端中执行）：查找并杀死占用端口的进程
lsof -i :18789 # 找到进程ID（PID），复制PID
kill -9 进程ID # 替换为找到的PID，杀死进程

# 杀死进程后，重新启动OpenClaw服务
node openclaw.mjs gateway --port 18789 --verbose

# 若仍失败，修改端口启动（如改为18790）
node openclaw.mjs gateway --port 18790 --verbose
```

---

### 问题4：浏览器访问"http://127.0.0.1:18789"提示"无法访问"

**原因：** OpenClaw服务未正常启动、端口未放行、防火墙拦截

**解决方案：**

1. 重新启动OpenClaw服务（执行`node openclaw.mjs gateway --port 18789 --verbose`）

2. 关闭电脑防火墙，重新访问

3. 检查端口是否放行，执行以下命令（Mac/Linux）：

```bash
sudo ufw allow 18789/tcp # 放行18789端口
sudo ufw reload # 重启防火墙
```

---

### 问题5：发送指令后，OpenClaw无响应、闪退

**原因：** 电脑内存不足、OpenClaw内存占用过高、依赖缺失

**解决方案：**

1. 关闭电脑中其他无用应用，释放内存

2. 限制OpenClaw内存占用，执行以下命令启动服务：

```bash
node openclaw.mjs gateway --port 18789 --memory-limit 2048 --verbose
```

3. 重新安装依赖，执行`pnpm install --force`，再次启动服务

---

### 问题6：Windows系统提示"权限不足，无法执行命令"

**原因：** 未以管理员身份打开PowerShell，导致无法执行安装、启动命令

**解决方案：** 关闭当前PowerShell，重新以"管理员身份"打开PowerShell，再次执行对应命令即可。

---

**恭喜！** 你已经完成了OpenClaw的本地部署，现在可以开始使用你的专属私人AI助理了！

# 安装完毕后测试智商
前往: https://moltbb.com

让bot们根据每天的实际工作写技术日记和文章，日记月累，自我提升