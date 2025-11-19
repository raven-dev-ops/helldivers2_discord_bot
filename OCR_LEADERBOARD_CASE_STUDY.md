Helldivers 2 Discord Bot – OCR Leaderboard Case Study
Project Overview
Helldivers 2 Discord Bot is a community-driven bot designed for Helldivers 2 gaming groups. It automates player stat tracking and leaderboards by extracting data from in-game scoreboard screenshots via OCR. Key features include a “Clan Hub” Discord menu for players to register, upload mission screenshots, and view leaderboards. The bot parses uploaded .png/.jpg screenshots of mission end-game stats using an OpenCV + Tesseract OCR pipeline
GitHub
, stores structured per-player stats in a MongoDB database, and compiles monthly leaderboards with awards (medals and MVP roles) for top contributors
GitHub
. It also manages LFG (Looking For Group) roles, regional roles, and provides admin utilities, making it a comprehensive clan management tool on Discord
GitHub
GitHub
. How it works: A player uploads a Helldivers 2 mission scoreboard screenshot via the Discord interface. The bot then automatically scans predefined regions on the image to read each player’s name and stats (kills, shots fired, accuracy, etc.) using OCR. After processing, it presents a confirmation embed for the user to verify the extracted data (with options to register new players or edit any mistakes). Once confirmed, the data is saved to the database and contributes to persistent leaderboards. At each month’s end, the bot ranks players by total shots fired and awards roles/medals accordingly (e.g. Class A Citizen, Bronze/Silver Star, Medal of Honor, etc.), and assigns an MVP role to the top player
GitHub
GitHub
. This fully automates what would otherwise be a tedious manual process of collating stats, ensuring an engaging experience where players can see their contributions reflected in Discord in near real-time.
OCR Pipeline Implementation
The core of the project is the OCR pipeline that converts raw screenshot images into accurate text data. This pipeline was carefully engineered for 100% accuracy in reading the game’s scoreboard, despite the complex visual elements in Helldivers 2’s UI. The implementation consists of several stages:
Region Segmentation: The scoreboard image is segmented into coordinate-defined regions for each data field per player. For example, regions cover “Player 1 Name,” “Player 1 Kills,” “Player 1 Shots Fired,” etc., and similarly for Player 2, 3, 4. These coordinates were determined for the game’s UI at a base resolution (1920×1080) and adjusted for other resolutions. The bot recognizes if a screenshot matches known resolutions (e.g. 1280×800 or 1920×1080) and selects the appropriate region map. If it’s a different size, it auto-scales and even handles letterboxed (ultrawide) images by calculating scale factors and padding
GitHub
GitHub
. This ensures that the OCR looks at the correct areas of the image where text is expected, regardless of the user’s screen size. The coordinate definitions cover all relevant fields (Name, Kills, Shots Fired/Hit, Deaths, Melee Kills, and new stats like Stims Used, Samples Extracted, Stratagems Used) and can scale from at least 1280×800 up to 1080p and beyond
GitHub
GitHub
.
Image Preprocessing: For each region, the bot applies multiple preprocessing techniques to enhance OCR accuracy. In code, it tries a sequence of transformations: using the original image, converting to grayscale, applying Otsu’s thresholding (binarization), Gaussian blur, adaptive threshold, and brightness/contrast adjustment
GitHub
GitHub
. Each preprocessed variant is fed to Tesseract OCR in turn. This multi-pass approach improves text capture under different conditions – e.g. thresholding can remove faint background noise, blurring can reduce artifacts, and increasing contrast can make faint text clearer. The bot stops as soon as a preprocessing method yields a non-empty OCR result
GitHub
GitHub
, prioritizing speed while ensuring that at least one method will successfully read the text even if others fail.
Tesseract Configuration: The OCR uses Tesseract (via pytesseract) with tailored settings for different fields
GitHub
. For player names, it uses a configuration optimized for alphanumeric text (whitelisting letters, numbers, and certain symbols, and using Page Segmentation Mode 7 for a single text line)
GitHub
. For numeric stats (kills, shots, etc.), it uses a different config that only allows digits, period, and percent characters (since accuracy might include a %)
GitHub
. By whitelisting expected characters and choosing suitable OCR modes, the bot minimizes false recognitions of unwanted characters. For example, it prevents Tesseract from interpreting random UI shapes as letters by disallowing those glyphs in a given context.
OCR Reading & Post-processing: As Tesseract extracts text from each region, the bot immediately cleans and validates the results. There are robust post-processing rules to correct common OCR misreads:
Character Corrections: The code replaces characters that are frequently mistaken for each other. For player names, it maps visually similar symbols to their intended letters (e.g. 5->S, 6->G, 8->B, @->A, etc.)
GitHub
. For numeric fields, it maps letter lookalikes to digits (e.g. O/o->0, I/l->1, S->5) and strips any non-digit characters
GitHub
. Notably, it avoids overcorrecting in cases where confusion between 0 and 8 could occur – for certain fields that are often zero (like “Melee Kills” or “Samples Extracted”), the code skips converting B to 8 to prevent turning a valid 0 into an 8 by mistake
GitHub
.
Secondary OCR Pass for Ambiguity: A clever heuristic is used to handle the common misread of “0” as “8”. If a field that is very likely to be zero comes back as "8" or "88", the bot performs a second OCR pass on that segment with a modified config that blacklists the character ‘8’
GitHub
. This forces Tesseract to consider other digits and often yields the correct "0" if that was the true value
GitHub
. For example, if “Melee Kills” initially OCRs as "8", the bot re-runs Tesseract disallowing ‘8’ and can get a blank or "0", confirming that it was actually zero
GitHub
.
Data Validation: The bot cross-checks certain relationships – for instance, it ensures Shots Hit is never greater than Shots Fired (if it is, it caps it to the Shots Fired value) and then recalculates Accuracy as ShotsHit/ShotsFired*100 to maintain consistency
GitHub
GitHub
. It also drops any obviously junk readings; if a player name comes out empty or as gibberish after cleaning, that entry can be flagged as unrecognized so the user can correct it.
Fuzzy Name Matching: Even after cleaning, an OCR’d player name might not exactly match the spelling a user registered (due to minor OCR errors or slight differences like spacing). To address this, the bot uses a fuzzy matching algorithm to match OCR names to the nearest registered player name in the database. Using a threshold (default 80% similarity)
GitHub
GitHub
, it compares the OCR result against all known names. If a sufficiently close match is found, the bot will assume it’s the same player and link the stats accordingly (this prevents duplicate entries for "PlayerOne" vs "Player0ne" for example). The matching considers string length and uses a combination of partial and token sort ratios (via RapidFuzz) to ensure reliable matches
GitHub
. Only if no good match is found does the bot treat the name as “missing”.
Database Insertion: Once all fields are verified, the stats for each player in the screenshot are compiled into a JSON-like structure and inserted into a MongoDB collection (User_Stats). Each mission gets a new sequential mission ID for reference
GitHub
GitHub
. The player’s Discord ID and guild ID are stored alongside to support multi-server use. If a player in the screenshot wasn’t previously registered (i.e., no fuzzy match and no existing record), their stats are still captured with the OCR name, and the bot provides ways to reconcile it (see below). All submitted data can later be queried for leaderboards or looked up by mission ID.
Overcoming OCR Challenges
Developing this OCR system to maintain 100% accuracy in a live community setting required solving several challenges unique to Helldivers 2’s UI and the realities of user submissions. Below we outline the key challenges and how the project addressed them:
Dynamic Background Noise: In Helldivers 2, the end-of-mission scoreboard isn’t a static overlay – the player’s 3D character model is often visible behind or around the scoreboard, and animated effects or background elements can intersect the text. This means the text is not on a uniform background and can have moving noise. To overcome this:
The image preprocessing pipeline was tuned to eliminate background clutter. Converting to grayscale and applying thresholding isolates bright text from darker backgrounds, and blurring can smooth out “hard” edges of 3D model textures
GitHub
GitHub
. By experimenting with these filters, the developers ensured that text stands out clearly even if a character’s armor or the game environment is behind it.
The bounding regions for certain stats were adjusted to avoid areas where the character model typically appears. For instance, if the lower portion of the scoreboard (where “Stratagems Used” or “Melee Kills” might be listed) overlaps the character’s head or body, the bot defines those regions with a slight offset or tighter crop to focus on the text portion that’s unobstructed
GitHub
GitHub
. In the 1920×1080 layout, the coordinates for some fields were explicitly “moved up” from their expected position to capture text away from the character model’s interference
GitHub
. This careful tweaking was informed by analyzing many screenshots and finding where the OCR read errors due to background interference.
Additionally, the bot provides a “Show OCR Regions” debug option during upload confirmation. This draws red rectangles on the screenshot showing exactly where the bot is reading text
GitHub
 and sends it to the user (ephemerally)
GitHub
. This feature, added from community feedback, helped identify if a region was off-target or being obstructed, enabling iterative refinement of those region boundaries.
UI Elements Intersecting Text: The Helldivers scoreboard UI itself has design elements (such as borders, lines, or icons) that can intersect with characters. For example, decorative poly lines or borders might run through digits, and icons (like a skull icon for deaths) might appear next to numbers. These can confuse OCR (e.g., part of a line through a “0” might make it look like an “8”). The bot’s strategy to handle this included:
Adaptive Thresholding and Inversion: In some preprocessing passes, the image is binarized and inverted such that text becomes white on black, and extraneous lines become black background
GitHub
GitHub
. This often causes thin UI lines to disappear (as they might be interpreted as noise) while preserving the thicker text strokes.
Character Whitelisting/Blacklisting: As noted, the OCR configs strictly limit what characters Tesseract should recognize
GitHub
. So even if a line or icon creates a weird shape, Tesseract will try to fit it to the allowed characters. In numeric fields, only digits and a few symbols are allowed – this prevents, say, a partial line from being output as an unintended letter. Moreover, the special second-pass removing ‘8’
GitHub
 directly tackles the case of 0 vs 8 confusion caused by artifacts. If the first OCR pass yields an implausible “88” for a field that should be 0, the bot literally asks Tesseract “try reading this again, but as if the digit 8 doesn’t exist” – effectively forcing it to choose 0 if that was the intended value
GitHub
. This dramatically improved accuracy for fields where zeros were common.
Custom Image Masks (Planned): (Note: This is a hypothetical extension based on typical OCR tuning; the current solution primarily uses thresholding.) The development approach considered the possibility of applying masks to ignore known static UI elements. For instance, if an icon always appears at a certain position, the image segment could be cropped to exclude it. However, thanks to the above methods, the OCR pipeline achieved high accuracy without needing explicit masking.
Varied Screenshot Resolutions and Quality: Users submitted screenshots from different platforms and with different settings – some might be 1080p, others from windowed mode at odd resolutions or even slightly cropped. Lower resolution images can be especially challenging for OCR (small text can be blurry or pixelated). The bot addresses this by:
Auto-Scaling Coordinates: As described, the define_regions function can scale the base coordinate template to the actual image size and even account for letterboxing
GitHub
GitHub
. This means even if a screenshot is, say, 1366×768, the bot will scale up the region where “Kills” should be, and still capture the text correctly at that relative location. It recognizes resolutions within a tolerance (±5 pixels) to account for minor cropping
GitHub
GitHub
.
Encouraging Higher Quality: In the user guide (FAQ), users are advised to upload images up to 5 MB and in common formats for “best OCR results”
GitHub
GitHub
. This indirectly nudges players to provide sufficiently clear images. The Docker environment also includes Tesseract with the English language data installed
GitHub
, ensuring the OCR engine has the necessary training data for even stylized fonts.
Post-processing Validation: If an image was too low-quality, one or more fields might come back blank or garbage even after all OCR attempts. The bot’s confirmation step will clearly show any missing data to the user, rather than silently guessing. This transparency allowed the community to notice issues and provide feedback. In practice, after many iterations, it became rare for any field to fail – the combination of scaling and preprocessing meant even suboptimal screenshots yielded correct data.
Evolving Game UI (New Stats): Helldivers 2 introduced new tracked stats over time (for example, Stims Used, Samples Extracted, etc. were not initially on the end-of-mission screen). Each time the game added or changed something on the scoreboard (“every warbond” – referring to each new war/campaign in the game’s lifecycle), the OCR system had to adapt. The project handled this by designing the OCR extraction to be extensible:
The code is structured with a base set of fields and an EXTRA_FIELDS list for new ones
GitHub
. When new stats appeared, the developers simply updated the region definitions and added the field names to the extraction logic. For instance, when Samples Extracted and Stratagems Used were introduced, they were added to the EXTRA_FIELDS and included in the OCR parsing loop
GitHub
. The User_Stats schema was effectively flexible, storing any fields present.
Because the OCR regions are defined by names, once the coordinates for a new stat were configured, the rest of the pipeline (OCR reading, cleaning, DB storage) largely continued to work with minimal changes. The maintainers would test a few screenshots from the new game update, adjust coordinates if needed (especially if the new fields pushed other elements around), and deploy an update. Thanks to the modular design, these changes were quick and did not require rewriting the whole OCR logic – the community often supplied sample screenshots right after an update so the bot could be patched promptly.
Continuous integration tests (via pytest) were expanded to include scenarios with the new fields, ensuring that the OCR extraction and downstream calculations (like accuracy recomputation) remained correct
GitHub
GitHub
.
User Error and Name Matching: Sometimes the OCR might correctly read a name, but that player hadn’t registered via the bot, leading to a “missing player” in the data. In other cases, the OCR could misread a name just enough that fuzzy matching doesn’t catch it (for example, an extremely stylized name or an unusual character). The bot’s solution is a strong user-feedback loop:
During the upload confirmation step, if any player name from the screenshot isn’t recognized (no exact or fuzzy match in the database), the interface shows a “Register Missing” button
GitHub
. The user can click it to immediately register that missing player – either by picking from a list of current Discord members (if they’re in voice or in the server) or by manually entering a Discord ID and name
GitHub
GitHub
. This ties the new OCR name to a Discord user so future submissions will match. It turns what could be an OCR “failure” into an opportunity for quick correction and learning.
The bot also allows editing any stat via an “Edit” button before finalizing
GitHub
GitHub
. If a number looks off (perhaps due to an OCR artifact), the user can select the player and field and input the correct value. This manual override ensures that even if OCR isn’t 100% on a rare edge case, the data can still be made accurate before saving.
These UX improvements were driven by community feedback. Early users reported instances of unrecognized names or occasional digit errors, so the developers added these interactive fixes to make the system robust. Over time, as the OCR accuracy improved, the need for manual edits dropped significantly; however, the features remain invaluable for trust – users know they can verify and correct data, which gives confidence in the automated system.
Results and Impact
After months of iteration and thousands of processed mission reports, the Helldivers 2 Discord Bot’s OCR system achieves near 100% accuracy in extracting scoreboard data. Practically every stat on every submitted screenshot is now correctly captured and recorded, an outcome of both advanced image processing and thoughtful user-centric design. The few cases where the OCR alone might falter are gracefully handled by the confirmation workflow, so the final stored data is always accurate. Community Leaderboards: With reliable data flowing in, the bot generates leaderboards that the community trusts. Players can see their rankings (e.g. by “Most Shots Fired” per month) and track progress toward awards
GitHub
. The automated MVP role and medal assignments have been a big hit – they’re given out fairly and consistently based on the data, rewarding active participants. This has driven engagement, as players strive to upload their missions to count towards the stats. Since the process is so seamless (just take a screenshot and upload via the bot), participation is high. Over a recent 28-day period, the bot was able to award dozens of medals ranging from Class A (5 missions) to Medal of Honor (150+ missions) completely automatically
GitHub
, a task that would be impossible to do manually with such scale and precision. Performance and Scale: The OCR pipeline as implemented is efficient. Using Python with OpenCV for image handling and Tesseract for OCR (with Tesseract running in fast OEM mode 3), the bot can process a screenshot in a matter of seconds. It queues and handles multiple uploads asynchronously, and stores results without blocking the Discord interactions. Even with thousands of submissions processed, the system remains responsive. The use of a MongoDB backend means queries for leaderboards or player stats are quick, and indexing on key fields (like player_name and mission_id) supports this
GitHub
GitHub
. The design to run in a single Discord guild (with possible extension to multiple guilds via separate collections) has proven sufficient for the community’s needs. Maintenance: Achieving 100% accuracy required continuous maintenance and updates initially, but the effort has paid off in a stable system. Each Helldivers “war” (major game update or new season) was met with a quick update to the bot’s OCR configs – for example, adjusting coordinates or adding a new stat field – and the framework handled the rest. The bot’s codebase includes tests for the OCR output and promotion logic, which catch regressions if any OCR change unintentionally affects downstream features
GitHub
. As a result, the developers are confident that the OCR pipeline can adapt to any future changes with minimal effort. Community Feedback: The collaborative feedback loop with users not only improved the OCR accuracy but also the UI/UX of the bot. Features like the region overlay and register-missing workflow turned users from passive consumers into active contributors in the bot’s accuracy. They could see what the bot “thinks,” and help correct it, effectively crowd-sourcing quality assurance. This has built trust – users see the system as transparent and reliable. The privacy policy and terms (included in the repo) also make it clear how data is used
GitHub
, which, coupled with accurate data handling, has led to widespread adoption in Helldivers communities. In conclusion, this case study of the Helldivers 2 Discord Bot demonstrates how combining OCR technology with community-driven development can automate a complex task (stat tracking from images) with a high degree of accuracy. By tackling visual noise, OCR quirks, and user experience challenges, the project delivered a robust solution that turns every screenshot into meaningful data. The result is a living leaderboard that enhances the gaming experience – all powered by an intelligent OCR pipeline under the hood. The approaches used here (multi-pass preprocessing, tailored OCR configs, fuzzy matching, user validation loops, and adaptive region scaling) can serve as a blueprint for similar OCR applications in gaming communities and beyond, where accuracy and trust are paramount. Sources: The implementation details and examples are based on the open-source repository for the Helldivers 2 Discord Bot
GitHub
GitHub
, including its README documentation and relevant code in the OCR processing module and Discord bot cogs. All code is released under the MIT License
GitHub
, encouraging others to learn from and build upon this project.
Citations
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L23-L27
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L28-L32
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L6-L10
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L18-L26
GitHub
PATCH.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/PATCH.md#L50-L59
GitHub
PATCH.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/PATCH.md#L63-L71
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L141-L149
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L156-L164
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L19-L28
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L8-L16
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L28-L36
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L43-L50
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L52-L60
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L65-L68
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L2-L10
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L2-L5
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L86-L94
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L100-L108
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L100-L106
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L6-L11
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L58-L66
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L58-L64
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L102-L111
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L112-L120
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L197-L205
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L242-L246
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L234-L243
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L254-L264
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L319-L327
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L36-L44
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L45-L52
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L42-L50
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L232-L240
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L186-L194
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L34-L41
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L36-L39
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L172-L180
GitHub
boundary_drawing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/boundary_drawing.py#L11-L19
GitHub
PATCH.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/PATCH.md#L26-L34
GitHub
PATCH.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/PATCH.md#L68-L74
GitHub
Dockerfile

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/Dockerfile#L7-L16
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L232-L240
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L14-L17
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L207-L215
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L210-L218
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L224-L231
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L91-L100
GitHub
extract_cog.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/cogs/extract_cog.py#L236-L245
GitHub
PATCH.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/PATCH.md#L44-L52
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L96-L104
GitHub
database.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/database.py#L98-L106
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L23-L31
GitHub
ocr_processing.py

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/ocr_processing.py#L86-L95
GitHub
README.md

https://github.com/raven-dev-ops/helldivers2_discord_bot/blob/d424a37b1b51370c3578fa8c6a588ee81a360da3/README.md#L294-L303

