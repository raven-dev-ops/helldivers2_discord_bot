Privacy Policy - Helldivers 2 Discord Bot (LFG and Mission Stats)
=================================================================

Last updated: 2025-10-17

This Privacy Policy describes how this Helldivers 2 Discord bot (the "Bot") processes information when it is invited to and used on a Discord server (the "Server"). The Bot is operated by the Server owner and/or bot maintainer (collectively, "we", "us", or "our").

The Bot's source code is open source and released under the MIT License. If you self-host your own instance of the Bot, you are the controller for any data processed by that deployment and should treat this policy as a template to adapt to your community and jurisdiction.

By using the Bot, you agree to this Privacy Policy. If you do not agree, do not use the Bot.


1. Information We Collect
-------------------------

The Bot only collects and stores the minimum information required to provide its features.

### 1.1 Discord account information

When you interact with the Bot, we may receive and store:

- Your Discord user ID
- Your Discord username and discriminator (for example, `Name#1234`) or handle
- Your current server nickname
- Your avatar URL (if required for embeds or logs)

This information is retrieved via the Discord API and stored where needed in MongoDB collections such as `Alliance` and `User_Stats`.

### 1.2 Registration data

When you use the registration form, we may store:

- Your Helldiver in-game name
- Optional ship name
- Optional region (for example, NA / EU / UK / AU / ASIA)
- Associated Discord IDs and guild IDs

This is used to:

- Match you correctly on leaderboards and stats
- Assign or update Discord roles (LFG ping role, region roles, and similar)

### 1.3 Mission statistics and screenshots

When you upload a scoreboard screenshot:

- The image is processed temporarily by the OCR pipeline (OpenCV and Tesseract)
- Parsed mission statistics (for example, shots fired, kills, deaths, accuracy, samples, stratagems) are stored in the database

Unless explicitly configured by the host, the Bot is intended to store only the extracted numeric/statistical data and metadata, not the raw screenshot. If your deployment stores screenshots, they are subject to your own hosting provider's policies.

### 1.4 Logs

The Bot writes logs to:

- The configured monitor channel (for operational messages and errors)
- The application log output of the hosting environment

Logs may include:

- Discord user IDs and usernames
- Error messages and stack traces
- Context (for example, which command or button was used)

Logs are used for debugging and moderation support.


2. How We Use Information
-------------------------

We use the collected information to:

- Provide Bot features such as registration, leaderboards, medals, and SOS / LFG utilities
- Maintain accurate mission and leaderboard data
- Assign and update roles (LFG, region, medal, MVP)
- Diagnose issues and prevent abuse

We do not sell or rent your data, and the Bot does not embed tracking or advertising code in Discord messages.


3. Data Sharing
---------------

We may share or disclose data:

- With the Server's administrators and moderators, to help manage the community
- With hosting providers (for example, database or cloud providers) as necessary to operate the Bot
- When required by law, court order, or to respond to lawful requests by public authorities

We do not otherwise share Bot data with third parties for marketing or advertising purposes.


4. Data Retention
-----------------

Data is retained for as long as reasonably necessary to:

- Maintain accurate stats and leaderboards
- Support historical mission data
- Assist with moderation and abuse prevention

Server owners or maintainers may periodically prune historical data or logs. If the Bot is removed from a server, existing stored data may remain in the database until manually deleted by the maintainer.


5. Your Choices and Rights
--------------------------

Because the Bot runs inside Discord, you can control your data primarily through:

- Discord account settings (for example, username, avatar, general privacy settings)
- Server membership (leaving the server stops new data collection by the Bot for that server)

You may also request, via the Server administrators or Bot maintainer, that:

- Your registration data be updated or corrected
- Your mission stats be edited (via the Bot's mission edit flow) or, where feasible, removed
- Your stored data (registration and/or stats) be deleted from the database

The feasibility and speed of such requests will depend on the Bot's deployment and the Server's policies.


6. Children's Privacy
---------------------

This Bot is intended for use only on servers that comply with Discord's Terms of Service, including age restrictions. We do not knowingly target or collect information from children under the minimum age specified by Discord or local law.


7. Security
-----------

We take reasonable technical and organizational measures to protect data, including:

- Using role and channel IDs rather than storing sensitive information where not needed
- Limiting stored data to operational necessities (IDs, names, stats)
- Relying on secure database connections (as provided by your MongoDB deployment)

However, no system is completely secure. Server owners and maintainers are responsible for:

- Protecting environment variables (for example, MongoDB URI and Discord token)
- Limiting access to hosting accounts and databases
- Choosing reputable hosting and database providers


8. Third-Party Services
-----------------------

The Bot depends on several external services and libraries, including but not limited to:

- Discord API (for events, commands, and user data)
- MongoDB or another compatible database provider
- Tesseract OCR (for processing screenshots)

These third parties have their own privacy policies and terms. We encourage you to review those documents separately.


9. Changes to This Policy
-------------------------

We may update this Privacy Policy from time to time. When we do, we will update the "Last updated" date at the top of this document. Material changes should be communicated to Server administrators so they can inform their communities.


10. Contact
-----------

If you have questions about this Privacy Policy or how the Bot handles your data, contact the Server owner or Bot maintainer through Discord (for example, via the monitor channel or an administrator).

If you are hosting your own copy of this Bot, you should customize this Privacy Policy (including contact information and retention practices) to match your deployment, your jurisdiction, and your community's needs. Nothing in this document constitutes legal advice.
