Clan Menu User Guide and FAQ

Overview
- This server uses a Clan Hub menu with buttons to register, upload mission stats, and edit submissions.
- Monthly leaderboards rank players by Most Shots Fired for the current month.
- At month end, submitters earn medals based on how many missions they submitted in the last 28 days, and the #1 ranked player earns the MVP role.

Clan Menu Buttons
- STORE: Sends a link to the GPT Fleet store.
- REGISTER: Opens a registration form to set your Helldiver name, optional ship name, and optionally set your Region. Grants the LFG PING! role automatically.
- UPLOAD MISSION: Starts the mission stats upload flow for a screenshot. Supports .png/.jpg/.jpeg up to 5 MB.
- EDIT MISSION: Opens a form to edit an existing mission by mission ID.

Registration
- Helldiver Name: Used to match you in leaderboards and stats. Use your exact in‑game name.
- Ship Name (optional): Stored on your profile and shown on leaderboards when available.
- Region (optional): Enter one of NA, EU, UK, AU, ASIA. If not provided, we auto‑detect from your Discord locale where possible. The bot assigns your region role and removes other region roles so you keep only one.
- LFG PING!: Assigned automatically on successful registration so you receive ping notifications for groups.
- You can re‑open REGISTER anytime to update Ship/Region; the bot will update roles accordingly.

Who Can Submit Stats
- Submitting stats requires the Class B Citizen role.
- If you see a message saying you must be a Class B Citizen, contact an admin to be approved.

How To Submit Mission Stats
1) Go to the Clan Hub menu and press UPLOAD MISSION.
2) You’ll be prompted to upload a scoreboard screenshot (.png/.jpg/.jpeg, up to 5 MB).
3) The bot OCRs the image and shows a confirmation embed with the recognized players and numbers.
4) If a player isn’t registered, use REGISTER MISSING from the view to register them on the spot.
5) Review the data and press YES to confirm. The bot saves the mission and posts a summary to the monitor channel.
6) You’ll see your mission ID in the confirmation message and monitor post (e.g., “Mission #0001234”).

Register Missing (During Upload)
- If a player name in the screenshot doesn’t match anyone in the database, the view will offer REGISTER MISSING.
- You can register missing players by providing their Discord ID and exact in‑game name.
- If you’re in a voice channel, the picker lets you pre‑fill a member’s Discord ID for convenience.

Editing a Mission
- Press EDIT MISSION in the menu and enter the mission ID.
- Pick the player and the specific field you want to edit.
- Enter values as numbers; Accuracy can be a percentage like 75.3%.
- Shots Hit cannot exceed Shots Fired; the bot re‑calculates Accuracy automatically.

Monthly Leaderboards
- Scope: The current calendar month.
- Ranking: By Most Shots Fired, then by games played as tiebreaker.
- Where: Posted in the leaderboard channel under the Clan Hub category (visibility may require Class B Citizen).
- Promotion Date: The embed includes “Promotions awarded on <Month DD, YYYY>” showing when month‑end awards run.

Submitter Medals (awarded monthly)
- What counts: Missions you submit (the person who confirms the upload).
- When counted: A rolling 28‑day window ending on promotion day.
- When awarded: Last day of the month (America/Chicago timezone).
- Tiers (roles are granted if you meet or exceed the tier):
  - Class A Citizen: 5 missions
  - Achievement Medal: 10 missions
  - Commendation: 25 missions
  - Bronze Star: 50 missions
  - Silver Star: 100 missions
  - Medal of Honor: 150 missions
- Announcement: The bot posts a congratulations message when awards are granted.

MVP Award (awarded monthly)
- On promotion day, the top‑ranked player on the leaderboard in each guild receives the MVP role.
- Any previous MVP holder in that guild has the MVP role removed.
- The bot posts an announcement with the new MVP.

Tips & Troubleshooting
- Name Matching: If OCR misses your name or it’s slightly different in‑game, use REGISTER to ensure your Helldiver name matches exactly.
- Missing Players: Use REGISTER MISSING during the upload confirmation.
- Can’t See Leaderboard: You may need the Class B Citizen role. Contact an admin.
- Region Role: Use REGISTER again to update Region. The bot removes old region roles and assigns the new one.
- File Limits: Upload .png/.jpg/.jpeg up to 5 MB for best OCR results.
- Accuracy Issues: The bot re‑computes Accuracy from Shots; if Shots Hit > Shots Fired, it caps to keep data valid.

FAQ
- Why a 28‑day window for submitter medals?
  - It keeps awards fair across months of different lengths and rewards consistent recent activity.
- What timezone is used for promotion day?
  - America/Chicago (Central Time).
- Do I need to register to appear on the leaderboard?
  - Yes, use REGISTER so your in‑game name and Discord are linked. Unregistered names won’t rank properly.
- How do I change my Region or Ship later?
  - Re‑open REGISTER from the menu and submit updated info.
- I got “You must be a Class B Citizen to submit stats.”
  - Ask an admin to grant you the Class B Citizen role.
- How do I find my mission ID to edit?
  - It’s shown in the confirmation message after saving and in the monitor channel summary.

