---
description: "Set up ManyChat DM automation for Instagram posts. Triggers: set up manychat, create dm automation, keyword automation"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# SKILL: ManyChat DM Automation

## PROCESS
1. Ask me: What is the keyword? (e.g., "GUIDE", "AIRDROP", "KRIB")
2. Ask me: What is the DM message? (the message sent when someone comments the keyword)
3. Ask me: What is the link to deliver? (Google Drive link, website link, Telegram link)
4. Generate a ManyChat automation config as JSON:

```json
{
  "name": "[KEYWORD] DM Automation",
  "keyword": "[KEYWORD]",
  "comment_replies": [
    "Sent! Check your DMs",
    "Just sent it! Check your inbox",
    "Done! Head to your DMs"
  ],
  "opening_dm": "Hey! Thanks for commenting [KEYWORD]. Here is what you requested:",
  "delivery_dm": "[DM message with link]",
  "follow_up_dm": "Did you get it? Let me know if you have questions.",
  "link_url": "[link]",
  "link_label": "[resource name]"
}
```

5. Save the config to 06-Drafts/manychat/[keyword]-config.json
6. Show me the full automation flow:
   - Someone comments "[KEYWORD]" on my Instagram post
   - ManyChat auto-replies with a random comment from comment_replies
   - ManyChat sends opening_dm via Instagram DM
   - ManyChat sends delivery_dm with the link
   - After 24 hours, ManyChat sends follow_up_dm

7. Tell me: "To deploy this automation, log into ManyChat (manychat.com), create a new Comment Automation, and paste these messages. Or if you have Playwright set up, I can deploy it automatically."

## PLAYWRIGHT AUTO-DEPLOY (optional, only if I ask)
If I say "deploy it automatically":
1. Write a Python script using Playwright that:
   - Opens manychat.com
   - Logs in (credentials from .env: MANYCHAT_EMAIL, MANYCHAT_PASSWORD)
   - Creates a new Comment Automation
   - Sets the keyword trigger
   - Adds comment replies
   - Sets up the DM flow (opening → delivery with link → follow-up)
   - Activates the automation
2. Save script to scripts/deploy-manychat.py
3. Run it and confirm deployment

## RULES
- Always show the full config before saving
- Never deploy automatically without explicit "deploy it" from me
- Comment replies should be varied (3 minimum)
- DM messages should feel personal, not robotic
- Always include a follow-up DM for engagement

## INTERACTION PATTERN

After presenting the automation flow, always say:

**"Automation flow ready. Approve, adjust, or give me specific instructions?"**

Then:
- If the user says "approved", "good", "done", or similar: save the config and finish
- If the user says "adjust" or gives edits: apply the edits, show the updated flow, and ask again
- If the user says "deploy it": run the Playwright auto-deploy process
- If the user gives specific instructions for a follow-up task (e.g., "now set up another one for KRIB"): apply those instructions immediately without asking again
- If the user gives BOTH edits AND instructions for a follow-up: apply both. Edit first, then execute the follow-up.
