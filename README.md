<div align="center">

# ⚙️ Core Bot

**An open-source, all-rounder application for any Discord community.**

![License: AGPL v3.0](https://img.shields.io/badge/License-AGPL_v3.0-blue.svg)
![Version](https://img.shields.io/badge/Version-v0.1--stable-orange.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Cloudflare](https://img.shields.io/badge/Cloudflare-Pages_Functions-F38020?logo=cloudflare&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)

[Features](#-key-features) • [Architecture](#%EF%B8%8F-tech-stack) • [Roadmap](#-roadmap) • [License](#-license) • [Support](#-issues--support)

• [Website](https://core-bot.pages.dev) •

---

</div>

## 📌 Introduction

Welcome to the official repository for **Core Bot**. Core is an initiative for a multi-purpose, open-source Discord bot built to empower server staff with quick moderation GUI tools, automated server security features, server insights, and engaging community utilities, all backed by a fast web dashboard.

The goal of this project is to build a high quality and reliable Discord bot with many free-to-use commands, features and customisation, available and accessible for everyone on Discord with publicly accessible source-code to encourage contributions.

### Keep in mind that the project is under active development and regularly updated with new features and improvements. This also implies that the bot can be unstable or can include bugs. For the highest security and stability, it is advised to use the latest stable version available on the website and in this repository.
---
## 🛡️ Key Features

* **🛡️ `/moderate` Dashboard:** One command to remember, with every moderation action bundled in an easy-to-use interactive graphical interface.
* **🚨 `/sentry` Defense System:** An automated, text 24/7 server protection utility against spammers and self-bots using trap channels.
* **📝 `/logging` Logging:** Log and record every moderation action (including warnings, mutes, kicks, bans, and their counteracts) in a desired channel.
* **⚙️ Dynamic Configuration and Storage:** Customizable guild preferences and user warnings are stored persistently in PostgreSQL.
* *(More features are being rolled out alongside major production releases.)*
---
## 🚧 Limitations

### ⚠️ The most recent commits are not implemented in the current website version.
Recent commits are for the new website version - still under maintenance - and lives under [https://v02a1.core-bot.pages.dev](https://v02a1.core-bot.pages.dev), which is not accessible to the public yet. The current [webpage](https://core-bot.pages.dev) is static, and features the essentials only, such as a Bot Invite Button, a Homepage, a Privacy Policy and a Terms Of Service. The navbar buttons (Commands, Premium, Support) do not work yet.

### ⚠️ There is no dashboard in the current version!
The interactive dashboard and web-level Discord integration is coming in a major future update.

### ⚠️ User warnings cannot be retrieved or deleted in the current version
User warnings are stored securely in the database system, however no commands are developed currently to remove or retrieve old warnings. This feature will be implemented in an update very soon.

---

## 🚀 Roadmap, Project Status, What's Planned

Core Bot is currently on main version **`v0.1-stable`**. The bot is publicly available for invitation to any server, with its current functions in a stable state. The dashboard will be featured in the next major upcoming update, since Discord OAuth2 and required backend integrations are still under maintenance.

- [x] Moderation commands (`/moderate`)
- [x] Anti-spam defense (`/sentry`)
- [x] Unique server settings and user warnings stored in Supabase
- [x] Public invite link release
- [x] Basic logging (`/logging`)
- [ ] User warning retrieval from database
- [ ] Complete Discord OAuth2 login integration
- [ ] Interactive Web Dashboard UI (`manage.html`)
- [ ] Web dashboard backend and Discord integration

---

## 📄 Privacy Policy & Data Handling

Core Bot does not save sensitive information regarding your Discord account, nor does the bot interact with any other social media accounts. User-related data, such as warnings or unique preferences are strictly associated to the *Discord User ID*, which are stored privately in the bot's database. Core processes only the minimum data necessary to operate server features and session security.

To thoroughly understand how your data is processed, please refer to our [Privacy Policy](https://core-bot.pages.dev/privacy-policy).

---

## 📜 License

Core Bot, its source code, and other related services are part of the open-source project licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Under the terms of AGPL-3.0, any modified and network hosted version of this codebase must also make its source code publicly available under the same license. For full terms, please refer to the [`LICENSE`](./LICENSE) file in this repository.


---

## 💬 Issues & Support

<pre style="white-space: pre-wrap; wrap-whitespace: true;">
Users who discover a bug (a.k.a. operational error or security flaw) are advised to report it promptly via <a href="https://discord.gg/N3t9gcmtD2">our support channel</a> by opening a ticket. Attempting to abuse bugs — or failing to report a known critical bug while actively benefiting from it — can result in access termination and blacklisting.
</pre>

### Intentionally exploiting, attempting to exploit, or benefiting from bugs, glitches, memory leaks, or unintended system mechanics within Core Bot is strictly prohibited.

---

<div align=center>

<h3>For inquiries, help, concerns, or if you'd like to follow the development and updates, you are welcome to join our Discord Server using the button below:<h3>

[![Discord Server](https://img.shields.io/badge/Core_Bot_Support-darkblue.svg?logo=discord&logoColor=white&color=5865F2)](https://discord.gg/N3t9gcmtD2)

</div>


<img width="1280" height="720" alt="Core_Bot_v0 1_GitHub_Release_260925" src="https://github.com/user-attachments/assets/ecf6730e-b4e3-48a1-9f97-b54de0f74b15" />
